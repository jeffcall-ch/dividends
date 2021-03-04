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

# define failed and operation list
failed = {}
operation_list = ["dividends", "splits", "cashflows", "incomes", "prices"]
for operation in operation_list:
    failed[operation] = []

START = time.monotonic()
request_time_list = []

url_main = [r"https://financialmodelingprep.com/api/v3/", r"https://fmpcloud.io/api/v3/"]
url_mid =  {"dividends" : r"historical-price-full/stock_dividend/",
            "splits"    : r"historical-price-full/stock_split/",
            "cashflows" : r"cash-flow-statement/",
            "incomes"   : r"income-statement/",
            "prices"    : r"quote-short/"}
url_end = [r"?apikey=606d643d87241cde956b5cd85a3c56d1"]



async def download_one(url, session, semaphore):

    await semaphore.acquire()
    diff_since_last_request = 100 #set difference to a big number to let first item to be sent quickly
    if len(request_time_list) >= 1:
        diff_since_last_request = request_time_list[-1] - (time.monotonic() - START)
    print (f"diff since last request {diff_since_last_request}")
    if diff_since_last_request < 0.1:
        await asyncio.sleep(0.1 - diff_since_last_request) #sleep 
    request_time_list.append(time.monotonic() - START)
    semaphore.release() # release semaphore to be able to start new request
    
    response = await session.get(url)
    resp_text = await response.text()
    print("Status:", response.status)
    # print("Content-type:", response.headers['content-type'])

async def bulk_donwload_url():
    async with ClientSession() as session:
        tasks = []
        semaphore = asyncio.Semaphore(value=1) # define to use ONE token only. One call at a time and release token only after certain waiting time
        for url in download_list:
            tasks.append(download_one(url, session, semaphore))
        await asyncio.gather(*tasks)


loop = asyncio.get_event_loop()
loop.run_until_complete(bulk_donwload_url())
print (request_time_list)
print (f"finished in  {time.monotonic() - START}")


