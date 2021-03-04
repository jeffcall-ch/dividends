import pandas as pd
from dividend_processor_offline import DividendProcessor as DivProc
import time
import csv
import logging
import sys
from SP500_div_yield_crawler import SP500

def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler('log.txt', mode='w')
    handler.setFormatter(formatter)
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(screen_handler)
    return logger
logger = setup_custom_logger('myapp')

start_time = time.time()

file_names = [r'\dividend.csv', r'\stock_split.csv', r'\cashflow.csv', r'\income.csv', r'\price.csv']

dividend = pd.read_csv(r'C:\Users\50000700\Python\Python_repos\dividends\excel_files' + file_names[0], index_col=[0])
# drop all rows, where the dividend is missing. However adjdividend may be present, but is not valueable for us.
dividend = dividend[dividend['dividend'].notna()]
stock_split = pd.read_csv(r'C:\Users\50000700\Python\Python_repos\dividends\excel_files' + file_names[1], index_col=[0])
cashflow = pd.read_csv(r'C:\Users\50000700\Python\Python_repos\dividends\excel_files' + file_names[2], index_col=[0])
income = pd.read_csv(r'C:\Users\50000700\Python\Python_repos\dividends\excel_files' + file_names[3], index_col=[0])
price = pd.read_csv(r'C:\Users\50000700\Python\Python_repos\dividends\excel_files' + file_names[4], index_col=[0])

ticker = 'O'

current_div_raw = dividend[dividend["Symbol"]==ticker].copy()
current_div_raw["Datetime"] = pd.to_datetime(current_div_raw['date'])
current_div_raw = current_div_raw.set_index('Datetime')
# current_div_raw.drop(current_div_raw.columns[1,2,3], axis=1, inplace=True)

current_price = price[price["Symbol"]==ticker]

current_split = stock_split[stock_split["Symbol"]==ticker]
current_split["Datetime"] = pd.to_datetime(current_split['date'])
current_split = current_split.set_index('Datetime')


current_divproc = DivProc(ticker, current_div_raw, current_price, current_split)
failed_to_process_list = []


dividend_freq_per_year = current_divproc.get_dividend_frequency_all_years()
corrigated_dividends = current_divproc.get_split_corrigated_dividends()
dividend_growth_per_year = current_divproc.get_dividend_growth_per_year()
dgr_3_5yr = current_divproc.get_DGR_3_5yr()
dividends_per_year = current_div_raw.resample("A")["dividend"].sum()
print (dividend_growth_per_year)
print (dgr_3_5yr)
print (dividends_per_year)
# dividends_per_year = current_divproc.get_dividends_per_year()
# forward_dividend = current_divproc.get_forward_dividend()
# dividend_yield = current_divproc.get_dividend_yield()
# dividend_growth_per_year = current_divproc.get_dividend_growth_per_year()
# dgr_3_5_yr = current_divproc.get_DGR_3_5yr()
