import pandas as pd
from dividend_processor_offline import DividendProcessor as DivProc
import time
import csv
import logging
import sys
from collections import namedtuple

pd.options.mode.chained_assignment = None  # default='warn'

def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler('log.txt', mode='w')
    handler.setFormatter(formatter)
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    # logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.addHandler(screen_handler)
    return logger
logger = setup_custom_logger('myapp')

start_time = time.time()

file_names = [r'\dividend.csv', r'\cashflow.csv', r'\income.csv', r'\price.csv']

dividend = pd.read_csv(r'C:\Users\50000700\Python\Python_repos\dividends\excel_files' + file_names[0])
cashflow = pd.read_csv(r'C:\Users\50000700\Python\Python_repos\dividends\excel_files' + file_names[1])
income = pd.read_csv(r'C:\Users\50000700\Python\Python_repos\dividends\excel_files' + file_names[2])
price = pd.read_csv(r'C:\Users\50000700\Python\Python_repos\dividends\excel_files' + file_names[3])

tickers = dividend.Symbol.unique()

failed_to_process_list = []
# Declaring namedtuple() 
# Stock_data = namedtuple('Stock_data',['symbol','dividend_raw','price', 'dividends_per_year', 'forward_dividend', 'dividend_yield', 'dividend_growth_per_year', 'dgr_3_5_yr']) 

structured_data = {}

for ticker in tickers:
    current_div_raw = dividend[dividend["Symbol"]==ticker]
    current_div_raw["Datetime"] = pd.to_datetime(current_div_raw['date'])
    current_div_raw = current_div_raw.set_index('Datetime')
    current_price = price[price["Symbol"]==ticker]

    current_divproc = DivProc(ticker, current_div_raw, current_price)
       
    try:
        dividends_per_year = current_divproc.get_dividends_per_year()
        forward_dividend = current_divproc.get_forward_dividend()
        dividend_yield = current_divproc.get_dividend_yield()
        dividend_growth_per_year = current_divproc.get_dividend_growth_per_year()
        dgr_3_5_yr = current_divproc.get_DGR_3_5yr()
        # structured_data[ticker] = [current_div_raw, dividends_per_year, dividend_yield, dividend_growth_per_year, dgr_3_5_yr]

        # current_stock_data = Stock_data(ticker, current_div_raw, current_price, dividends_per_year, forward_dividend, dividend_yield, dividend_growth_per_year, dgr_3_5_yr)
    except Exception as Argument:  
        failed_to_process_list.append(ticker)
        logger.info(Argument)

# print (len(structured_data))
     
with open(r'C:\Users\50000700\Python\Python_repos\dividends\excel_files\failed_to_process.csv', 'w', newline='') as failed_file:
    writer = csv.writer(failed_file)
    writer.writerow(["No", "Symbol"])
    for i, symbol in enumerate(failed_to_process_list):
        writer.writerow([i+1, symbol])

print (f"overall runtime {time.time() - start_time}")
