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


symbols = ["ADP","ADM", "AFL", "AAPL", "FASZ", "GECI"]
download_list = ["https://financialmodelingprep.com/api/v3/historical-price-full/stock_dividend/AAPL?apikey=606d643d87241cde956b5cd85a3c56d1", 
"https://financialmodelingprep.com/api/v3/historical-price-full/stock_dividend/O?apikey=606d643d87241cde956b5cd85a3c56d1", 
"https://financialmodelingprep.com/api/v3/historical-price-full/stock_dividend/MSFT?apikey=606d643d87241cde956b5cd85a3c56d1", 
"https://financialmodelingprep.com/api/v3/historical-price-full/stock_dividend/JPM?apikey=606d643d87241cde956b5cd85a3c56d1",
"https://financialmodelingprep.com/api/v3/historical-price-full/stock_dividend/KO?apikey=606d643d87241cde956b5cd85a3c56d1",
"https://financialmodelingprep.com/api/v3/historical-price-full/stock_dividend/AAPL?apikey=606d643d87241cde956b5cd85a3c56d1", 
"https://financialmodelingprep.com/api/v3/historical-price-full/stock_dividend/O?apikey=606d643d87241cde956b5cd85a3c56d1", 
"https://financialmodelingprep.com/api/v3/historical-price-full/stock_dividend/MSFT?apikey=606d643d87241cde956b5cd85a3c56d1", 
"https://financialmodelingprep.com/api/v3/historical-price-full/stock_dividend/JPM?apikey=606d643d87241cde956b5cd85a3c56d1",
"https://financialmodelingprep.com/api/v3/historical-price-full/stock_dividend/KO?apikey=606d643d87241cde956b5cd85a3c56d1"]

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
    print (f"diff since last request {diff_since_last_request}")
    if diff_since_last_request < 0.075:
        await asyncio.sleep(0.075 - diff_since_last_request) #sleep 
    # request_time_list.append(time.monotonic() - START)
    semaphore.release() # release semaphore to be able to start new request
    url = url_main[0] + url_mid[operation] + symbol + url_end
    url_main_list.append(url_main[0])
    request_time_list.append(time.monotonic() - START)

    try:
        # print (f"request sent: {time.monotonic() - START}")
        response = await session.get(url)
        resp_text = await response.text()
        print (url)
        # print("Status:", response.status)
        if response.status != 200:
            failed["html_response"].append([symbol, operation])
        if operation in ["dividends", "splits"]:
            df = process_dividends_stocksplits(resp_text)
        else:
            df = pd.DataFrame(json.loads(resp_text))
        
        # further processing of df
        if operation in ["prices"]:
            df["Symbol"] = symbol
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
            else:
                df = df.set_index('Datetime')
                df["Symbol"] = symbol

        dataframes[operation] = pd.concat([dataframes[operation], df], ignore_index=True, sort=False)

        print (f"symbol: {symbol} operation: {operation} status: {response.status}")
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
            print (symbol)
            for operation in operation_list:
                # tasks.append(download_one(url, session, semaphore))
                tasks.append(download_one_item(session, semaphore, symbol, operation))
        await asyncio.gather(*tasks)


loop = asyncio.get_event_loop()
# loop.run_until_complete(bulk_donwload_url())
loop.run_until_complete(bulk_donwload_symbols())
print (f"number of requests {len(request_time_list)}")
print (request_time_list)
print (url_main_list)
print (f"finished in  {time.monotonic() - START}")
print (failed)


for operation in operation_list:
    output_main = r"C:\Users\50000700\Python\Python_repos\dividends\excel_files\\"
    output_end = r'.csv'
    output_path = output_main + operation + output_end
    dataframes[operation].to_csv(output_path, mode='a', header=not os.path.exists(output_path))












# async def download_one(url, session, semaphore):
#     await semaphore.acquire()
#     diff_since_last_request = 100 #set difference to a big number to let first item to be sent quickly
#     if len(request_time_list) >= 1:
#         diff_since_last_request = request_time_list[-1] - (time.monotonic() - START)
#     print (f"diff since last request {diff_since_last_request}")
#     if diff_since_last_request < 0.1:
#         await asyncio.sleep(0.1 - diff_since_last_request) #sleep 
#     request_time_list.append(time.monotonic() - START)
#     semaphore.release() # release semaphore to be able to start new request
#     response = await session.get(url)
#     resp_text = await response.text()
#     print("Status:", response.status)
#     print("Content-type:", response.headers['content-type'])

# async def bulk_donwload_url():
#     async with ClientSession() as session:
#         tasks = []
#         semaphore = asyncio.Semaphore(value=1) # define to use ONE token only. One call at a time and release token only after certain waiting time
#         for url in download_list:
#             # tasks.append(download_one(url, session, semaphore))
#             tasks.append(download_one_item(session, semaphore, symbol, operation))
#         await asyncio.gather(*tasks)
