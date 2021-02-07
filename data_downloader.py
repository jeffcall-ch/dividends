from fmp_python.fmp import FMP
import pathlib
import pandas as pd
from datetime import datetime
import os
import numpy as np
import time
import csv

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
ticker_list = df['TickerSymbol'].tolist()
# print (len(ticker_list))

os.environ["FMP_API_KEY"] = "606d643d87241cde956b5cd85a3c56d1"
fmp = FMP()

def get_dividend_df_of(symbol):
    # dividend, date  - historical dividend values and dates
    dividends_raw = fmp.get_dividends(symbol, 'historical-price-full/stock_dividend')
    # set proper DateTime object as the index of the dataframe
    dividends_raw['Datetime'] = pd.to_datetime(dividends_raw['date'])
  
    try:
        # find days difference between rows. Needed to see data gap (for instane AAPL dividends)
        dividends_raw['Datetime_DaysDiffRows']=dividends_raw['Datetime'].diff().dt.days
        # find if there is more than 365 days passed between rows. If that happens, delete all rows below
        index_of_first_gap = np.where(dividends_raw['Datetime_DaysDiffRows'].lt(-365))[0][0]
        dividends_raw = dividends_raw.iloc[:index_of_first_gap]
    except: 
        # no gaps found in datetime
        pass
    
    dividends_raw = dividends_raw.set_index('Datetime')
    dividends_raw["Symbol"] = symbol
    return dividends_raw
    

def get_cf_statement_of(symbol):
    # freeCashFlow
    # dividendsPaid
    cfStatement = fmp.get_data_from_api('ABT', 'cash-flow-statement')
    # set proper DateTime object as the index of the dataframe
    cfStatement['Datetime'] = pd.to_datetime(cfStatement['date'])
    cfStatement = cfStatement.set_index('Datetime')
    cfStatement["Symbol"] = symbol
    return cfStatement

def get_income_statement_of(symbol):
    # eps
    # epsdiluted
    incomeStatement = fmp.get_data_from_api('ABT', 'income-statement')
    # set proper DateTime object as the index of the dataframe
    incomeStatement['Datetime'] = pd.to_datetime(incomeStatement['date'])
    incomeStatement = incomeStatement.set_index('Datetime')
    incomeStatement["Symbol"] = symbol
    return incomeStatement

request_counter = 0
start_time = time.time()
overall_start_time = time.time()
download_counter = 0

# ticker_list = ["ADP","ADM", "AFL", "AAPL", "FASZ", "GECI"]
failed_to_download_list = []

dividend = get_dividend_df_of("AAPL")
cashflow = get_cf_statement_of("AAPL")
income = get_income_statement_of("AAPL")


for ticker in ticker_list:
    if ticker == "AAPL":
        continue
    request_start_time = time.time()
    # 10 requests per second are allowed
    request_counter += 1
    download_counter += 1
    print (download_counter)
    if request_counter >= 10 :
        request_counter = 0
        # print ("reached 10 requests")
        # print("--- %s seconds ---" % (time.time() - start_time))
        if (time.time() - start_time) < 1 :
            # print ("reached 10 requests waiting 1 second")
            # print("--- %s seconds ---" % (time.time() - start_time))
            time.sleep(1)
            start_time = time.time()
    
    # current_dividend  = get_dividend_df_of(ticker)
    # print (current_dividend)
    # current_cashflow = get_cf_statement_of(ticker)
    # current_income = get_income_statement_of(ticker)
    # dividend = pd.concat([dividend, current_dividend], ignore_index=True, sort=False)
    # print (dividend)
    # cashflow = pd.concat([cashflow, current_cashflow], ignore_index=True, sort=False)
    # income = pd.concat([income, current_income], ignore_index=True, sort=False)

    try:
        current_dividend  = get_dividend_df_of(ticker)
        current_cashflow = get_cf_statement_of(ticker)
        current_income = get_income_statement_of(ticker)
        dividend = pd.concat([dividend, current_dividend], ignore_index=True, sort=False)
        cashflow = pd.concat([cashflow, current_cashflow], ignore_index=True, sort=False)
        income = pd.concat([income, current_income], ignore_index=True, sort=False)
              
    except:
        print ("ERROR")
        print (f"symbol cannot be downloaded check separately: {ticker}")
        failed_to_download_list.append(ticker)
        continue

file_names = [r'\dividend.csv', r'\cashflow.csv', r'\income.csv']
dataframes = [dividend, cashflow, income]

for i, dataframe in enumerate(dataframes):
    output_path = r'C:\Users\50000700\Python\Python_repos\dividends\excel_files' + file_names[i]
    dataframe.to_csv(output_path, mode='a', header=not os.path.exists(output_path))

with open(r'C:\Users\50000700\Python\Python_repos\dividends\excel_files\failed.csv', 'w', newline='') as failed_file:
    writer = csv.writer(failed_file)
    writer.writerow(["No", "Symbol"])
    for i, symbol in enumerate(failed_to_download_list):
        writer.writerow([i+1, symbol])

# print ("dividends")
# print (dividend)

# print ("cashflow")
# print (cashflow)

# print ("income")
# print (income)

print ("  ****  ")
print (f"overall runtime {time.time() - overall_start_time}")
print (f"symbols couldn't be downloaded : {failed_to_download_list}")


