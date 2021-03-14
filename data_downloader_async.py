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
import json 

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
symbols = df['TickerSymbol'].tolist()

# symbols = ["A","AAN","AAPL","ABBV","ABC","ABM","ABR","ABT","ACC","ACN","ADC","ADI","ADM","ADP","AEE","AEL","AEM","AEP","AES","AFG","AFL","AGCO","AGM","AGO","AIRC","AIT","AIZ","AJG","AL","ALB","ALE","ALG","ALL","ALLE","ALLY","ALRS","ALTA","AMGN","AMNB","AMP","AMSF","AMT","ANDE","ANTM","AON","AOS","APD","APH","APLO","APOG","AQN","ARE","AROW","ARTNA","ASB","ASH","ATLO","ATO","ATR","ATRI","ATVI","AUB","AUBN","AVA","AVB","AVGO","AVNT","AVT","AVY","AWK","AWR","AXP","AXS","BAC","BAH","BAM","BANF","BANR","BBY","BC","BCPC","BDL","BDX","BEN","BEP","BF-B","BHB","BIP","BK","BKH","BKSC","BKUTK","BLK","BMI","BMRC","BMTC","BMY","BOKF","BORT","BPOP","BPY","BR","BRC","BRO","BSRR","BUSE","BWFG"]

# define empty dataframes
dividends = pd.DataFrame()
splits = pd.DataFrame()
cashflows = pd.DataFrame()
incomes = pd.DataFrame()
prices = pd.DataFrame()

dataframes = {"dividends" : dividends,
              "splits"    : splits,
              "cashflows" : cashflows,
              "incomes"   : incomes,
              "prices"    : prices}



# define failed and operation list
failed = {}
operation_list = ["dividends", "splits", "cashflows", "incomes", "prices"]
for operation in operation_list:
    failed[operation] = []
failed["html_response"] = []

START = time.monotonic()
request_time_list = []
url_main_list = []

url_main = [r"https://financialmodelingprep.com/api/v3/", r"https://fmpcloud.io/api/v3/"]
url_mid =  {"dividends" : r"historical-price-full/stock_dividend/",
            "splits"    : r"historical-price-full/stock_split/",
            "cashflows" : r"cash-flow-statement/",
            "incomes"   : r"income-statement/",
            "prices"    : r"quote-short/"}
url_end = r"?apikey=606d643d87241cde956b5cd85a3c56d1"


async def download_one_item(session, semaphore, symbol, operation):
    await semaphore.acquire()
    diff_since_last_request = 100 #set difference to a big number to let first item to be sent quickly
    if len(request_time_list) >= 1:
        diff_since_last_request = request_time_list[-1] - (time.monotonic() - START)
        if url_main_list[-1] == url_main[0]:
            url_main.reverse()
    if len(request_time_list) % 100 == 0:
        print (len(request_time_list))
    # print (f"diff since last request {diff_since_last_request}")
    if diff_since_last_request < 0.053:
        await asyncio.sleep(0.053 - diff_since_last_request) #sleep
    if len(request_time_list) % 4 == 0:
        await asyncio.sleep(0.14) # Nginx web server of FMP has an interval of 0.05 with a burst of 5 to protect against any server attack. Testing a lot shows working: 0.053 diff and 0.14 waiting after every 4th request
    request_time_list.append(time.monotonic() - START)
    semaphore.release() # release semaphore to be able to start new request
    url = url_main[0] + url_mid[operation] + symbol + url_end
    url_main_list.append(url_main[0])
    request_time_list.append(time.monotonic() - START)

    try:
        # print (f"request sent: {time.monotonic() - START}")
        response = await session.get(url)
        resp_text = await response.text()
        # print (url)
        # print("Status:", response.status)
        if response.status != 200:
            failed["html_response"].append([symbol, operation, response.status])
        if operation in ["dividends", "splits"]:
            df = process_dividends_stocksplits(resp_text)
        else:
            df = pd.DataFrame(json.loads(resp_text))
        
        # further processing of df
        if operation in ["prices"]:
            pass  # no extra adjustment here
        else:
            df['Datetime'] = pd.to_datetime(df['date'])
            if operation in ["dividends"]:
                try:
                    # find days difference between rows. Needed to see data gap (for instane AAPL dividends)
                    df['Datetime_DaysDiffRows']=df['Datetime'].diff().dt.days
                    # find if there is more than 400 days passed between rows. If that happens, delete all rows below
                    index_of_first_gap = np.where(df['Datetime_DaysDiffRows'].lt(-400))[0][0]
                    df = df.iloc[:index_of_first_gap]
                except: 
                    # no gaps found in datetime
                    pass
                df["Symbol"] = symbol
            else:
                df = df.set_index('Datetime')

        df["Symbol"] = symbol # add symbol column
        dataframes[operation] = pd.concat([dataframes[operation], df], ignore_index=True, sort=False)

        # print (f"symbol: {symbol} operation: {operation} status: {response.status}")
        # print("Status:", response.status)
        # print (f"downloaded and coverted df:  {df}")
        if resp_text == "[ ]": # in case the response is empty - not in database
            failed[operation].append(symbol)
    except:
        failed[operation].append(symbol)

def process_dividends_stocksplits(response_text):
    starter_char = response_text.find(" [ ")
    end_char = response_text.find(" ]")
    formatted_text = response_text[(starter_char):(end_char+2)].strip()
    formatted_text.rstrip('\r\n')
    formatted_text.lstrip('\r\n')
    # print (formatted_text)
    formatted_json = json.loads(formatted_text)
    return pd.DataFrame(formatted_json)

async def bulk_donwload_symbols():
    async with ClientSession() as session:
        tasks = []
        semaphore = asyncio.Semaphore(value=1) # define to use ONE token only. One call at a time and release token only after certain waiting time
        for symbol in symbols:
            # print (symbol)
            for operation in operation_list:
                # tasks.append(download_one(url, session, semaphore))
                tasks.append(download_one_item(session, semaphore, symbol, operation))
        await asyncio.gather(*tasks)

loop = asyncio.get_event_loop()
# loop.run_until_complete(bulk_donwload_url())
loop.run_until_complete(bulk_donwload_symbols())
print (f"number of requests {len(request_time_list)}")
# print (request_time_list)
# print (url_main_list)
print (f"finished in  {time.monotonic() - START}")
# print (failed)

for operation in operation_list:
    output_main = r"C:\Users\50000700\Python\Python_repos\dividends\excel_files\\"
    output_end = r'.csv'
    output_path = output_main + operation + output_end
    dataframes[operation].to_csv(output_path, mode='w', header=not os.path.exists(output_path))

with open(r'C:\Users\50000700\Python\Python_repos\dividends\excel_files\failed.csv', 'w', newline='') as failed_file:
    writer = csv.writer(failed_file)
    writer.writerow(["No", "Symbol", "Operation"])
    for failed_operation in failed:
        for i, symbol in enumerate(failed[failed_operation]):
            writer.writerow([i+1, symbol, failed_operation])