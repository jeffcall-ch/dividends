from fmp_python.fmp_async import FMP
import pathlib
import pandas as pd
from datetime import datetime
import os
import numpy as np
import time
import csv
import aiohttp
from aiohttp import ClientSession
import asyncio 

python_repo_home_folder = pathlib.Path.home() / "Python" / "Python_repos" / "dividends"
dripinvesting_folder = python_repo_home_folder / "excel_files" / "dripinvesting"

def getListOfFiles(dirName):
    listOfFile = os.listdir(dirName)
    allFiles = list()
    for entry in listOfFile:
        fullPath = os.path.join(dirName, entry)
        if os.path.isfile(fullPath):
            allFiles.append(fullPath)       
    return allFiles     

# import latest dripinvesting excel file into pandas
listOfFiles = getListOfFiles(dripinvesting_folder.as_posix())

# read the excel file
# combine rows 4-5 to be the header. By doing this the real pandas df will start from the header (and you don't need to drop rows..)
# note that in case the top cell is empty, then it will use the closest top cell value to the left.
# EXAMPLE: "TickerSymbol" column (col "B" in excel) name is correct. But the next column is empty top cell and "Sector" bottom cell (col "C" in excel). 
#           Now it will be "TickerSector"
df = pd.read_excel(listOfFiles[0], sheet_name='All CCC', header=[4,5])
# flatten the multi index header: https://stackoverflow.com/questions/41931332/how-do-i-flatten-a-hierarchical-column-index-in-a-pandas-dataframe
df.columns = df.columns.map(lambda x: ''.join([*map(str, x)]))
# drop last rows of summary where not individual companies are shown but sector performance
df = df.dropna(subset=['TickerSector'])


# ticker_list = df['TickerSymbol'].tolist()
ticker_list = ["ADP","ADM", "AFL", "AAPL", "FASZ", "GECI"]



# define empty dataframes
dividend = pd.DataFrame()
stock_split = pd.DataFrame()
cashflow = pd.DataFrame()
income = pd.DataFrame()
latest_price = pd.DataFrame()

# define failed list
failed = {}
# define operation list
operation_list = ["dividend", "cf_statement", "income_statement", "stock_split", "price"]
for operation in operation_list:
    failed[operation] = []

async def semaphore_and_wait(semaphore):
    # function to put delay between requests. Default delay is 0.1 sec
    await semaphore.acquire()
    diff_since_last_request = 100 #set difference to a big number to let first item to be sent quickly
    if len(request_time_list) >= 1:
        diff_since_last_request = request_time_list[-1] - (time.monotonic() - START)
    print (f"diff since last request {diff_since_last_request}")
    if diff_since_last_request < 0.1:
        await asyncio.sleep(0.1 - diff_since_last_request) #sleep 
    request_time_list.append(time.monotonic() - START)
    print (request_time_list)
    semaphore.release() # release semaphore to be able to start new request

async def get_dividend_df_of(symbol, fmp, semaphore):
    # dividend, date  - historical dividend values and dates
    semaphore_and_wait(semaphore)
    try:
        dividends_raw = await fmp.get_dividends_and_stock_splits(symbol, 'historical-price-full/stock_dividend')
    except:
        failed["dividend"].append(symbol)
        return

    # set proper DateTime object as the index of the dataframe
    dividends_raw['Datetime'] = pd.to_datetime(dividends_raw['date'])
  
    try:
        # find days difference between rows. Needed to see data gap (for instane AAPL dividends)
        dividends_raw['Datetime_DaysDiffRows']=dividends_raw['Datetime'].diff().dt.days
        # find if there is more, than 400 days passed between rows. If that happens, delete all rows below
        index_of_first_gap = np.where(dividends_raw['Datetime_DaysDiffRows'].lt(-400))[0][0]
        dividends_raw = dividends_raw.iloc[:index_of_first_gap]
    except: 
        # no gaps found in datetime
        pass
    
    dividends_raw = dividends_raw.set_index('Datetime')
    dividends_raw["Symbol"] = symbol
    global dividend
    dividend = pd.concat([dividend, dividends_raw], ignore_index=True, sort=False)

async def get_stock_split_df_of(symbol, fmp, semaphore):
    # returns stock splits
    semaphore_and_wait(semaphore)
    try:
        stock_splits = await fmp.get_dividends_and_stock_splits(symbol, 'historical-price-full/stock_split')
    except:
        failed["stock_split"].append(symbol)
        return
    # set proper DateTime object as the index of the dataframe
    stock_splits['Datetime'] = pd.to_datetime(stock_splits['date'])
    stock_splits = stock_splits.set_index('Datetime')
    stock_splits["Symbol"] = symbol
    global stock_split
    stock_split = pd.concat([stock_split, stock_splits], ignore_index=True, sort=False)
    
async def get_cf_statement_of(symbol, fmp, semaphore):
    # freeCashFlow
    # dividendsPaid
    semaphore_and_wait(semaphore)
    try:
        cfStatement = await fmp.get_data_from_api(symbol, 'cash-flow-statement')
    except:
        failed["cf_statement"].append(symbol)
        return
    # set proper DateTime object as the index of the dataframe
    cfStatement['Datetime'] = pd.to_datetime(cfStatement['date'])
    cfStatement = cfStatement.set_index('Datetime')
    cfStatement["Symbol"] = symbol
    global cashflow
    cashflow = pd.concat([cashflow, cfStatement], ignore_index=True, sort=False)

async def get_income_statement_of(symbol, fmp, semaphore):
    # eps
    # epsdiluted
    semaphore_and_wait(semaphore)
    try:
        incomeStatement = await fmp.get_data_from_api(symbol, 'income-statement')
    except:
        failed["income_statement"].append(symbol)
        return
    # set proper DateTime object as the index of the dataframe
    incomeStatement['Datetime'] = pd.to_datetime(incomeStatement['date'])
    incomeStatement = incomeStatement.set_index('Datetime')
    incomeStatement["Symbol"] = symbol
    global income
    income = pd.concat([income, incomeStatement], ignore_index=True, sort=False)

async def get_latest_price_of(symbol, fmp, semaphore):
    semaphore_and_wait(semaphore)
    try:
        real_time_price = await fmp.get_quote_short(symbol)
    except:
        failed["price"].append(symbol)
        return
    real_time_price["Symbol"] = symbol
    global latest_price
    latest_price = pd.concat([latest_price, real_time_price], ignore_index=True, sort=False)

async def create_starter_dfs(fmp, semaphore):
    global dividend
    global stock_split
    global cashflow
    global income
    global latest_price
    semaphore_and_wait(semaphore)
    dividend = await get_dividend_df_of("AAPL", fmp, semaphore)
    semaphore_and_wait(semaphore)
    stock_split = await get_stock_split_df_of("AAPL", fmp, semaphore)
    semaphore_and_wait(semaphore)
    cashflow = await get_cf_statement_of("AAPL", fmp, semaphore)
    semaphore_and_wait(semaphore)
    income = await get_income_statement_of("AAPL", fmp, semaphore)
    semaphore_and_wait(semaphore)
    latest_price = await get_latest_price_of("AAPL", fmp, semaphore)

async def bulk_donwload():
    async with ClientSession() as session:
        tasks = []
        semaphore = asyncio.Semaphore(value=1) # define to use ONE token only. One call at a time and release token only after certain waiting time
        os.environ["FMP_API_KEY"] = "606d643d87241cde956b5cd85a3c56d1"
        fmp = FMP(session)
        
        for ticker in ticker_list:
            # if ticker == "AAPL":
            #     continue
            tasks.append(create_starter_dfs(fmp, semaphore))
            tasks.append(get_dividend_df_of(ticker, fmp, semaphore))
            tasks.append(get_cf_statement_of(ticker, fmp, semaphore))
            tasks.append(get_income_statement_of(ticker, fmp, semaphore))
            tasks.append(get_stock_split_df_of(ticker, fmp, semaphore))
            tasks.append(get_latest_price_of(ticker, fmp, semaphore))
        await asyncio.gather(*tasks)
        
def write_files():
    global dividend
    global stock_split
    global cashflow
    global income
    global latest_price
    global failed
    file_names = [r'\dividend.csv', r'\stock_split.csv', r'\cashflow.csv', r'\income.csv', r'\price.csv']
    dataframes = [dividend, stock_split, cashflow, income, latest_price]

    for i, dataframe in enumerate(dataframes):
        output_path = r'C:\Users\50000700\Python\Python_repos\dividends\excel_files' + file_names[i]
        dataframe.to_csv(output_path, mode='a', header=not os.path.exists(output_path))

    with open(r'C:\Users\50000700\Python\Python_repos\dividends\excel_files\failed.csv', 'w', newline='') as failed_file:
        writer = csv.writer(failed_file)
        writer.writerow(["No", "Symbol", "Operation"])
        for failed_operation in failed:
            for i, symbol in enumerate(failed[failed_operation]):
                writer.writerow([i+1, symbol, failed_operation])

request_time_list = []
START = time.monotonic()
loop = asyncio.get_event_loop()
loop.run_until_complete(bulk_donwload())
print (request_time_list)
# write_files()

# print ("  ****  ")
# print (f"symbols couldn't be downloaded : {failed}")
