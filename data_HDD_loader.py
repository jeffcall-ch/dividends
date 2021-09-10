import pandas as pd
from dividend_processor_offline_adjDiv import DividendProcessor as DivProc
import time
import csv
import logging
import sys
from SP500_div_yield_crawler import SP500

pd.options.mode.chained_assignment = None  # default='warn'

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

file_names = [r'\dividends.csv', r'\splits.csv', r'\cashflows.csv', r'\incomes.csv', r'\prices.csv']

dividend = pd.read_csv(r'C:\Users\50000700\Python\Python_repos\dividends\excel_files' + file_names[0])
stock_split = pd.read_csv(r'C:\Users\50000700\Python\Python_repos\dividends\excel_files' + file_names[1])
cashflow = pd.read_csv(r'C:\Users\50000700\Python\Python_repos\dividends\excel_files' + file_names[2])
income = pd.read_csv(r'C:\Users\50000700\Python\Python_repos\dividends\excel_files' + file_names[3])
price = pd.read_csv(r'C:\Users\50000700\Python\Python_repos\dividends\excel_files' + file_names[4])

# crawl S&P500 dividend yield from https://www.multpl.com/s-p-500-dividend-yield
# sp500 = SP500()
# sp500_div_yield = sp500.get_dividend_yield()

sp500_div_yield = 1.48
div_yield_min = 1.5 * sp500_div_yield
div_yield_max = 5 * sp500_div_yield
# div_yield sweet spot is between 4% and 7%
# set min and max values accordingly
# set minimum years of constant dividend increase wihtout cut
sweet_low = 4
sweet_high = 7
sweet_total_return = 9
minimum_years_of_div_increase = 10


if div_yield_min <= sweet_low and sweet_low <= div_yield_max:
    div_yield_min = sweet_low
if div_yield_min <= sweet_high and sweet_high <= div_yield_max:
    div_yield_max = sweet_high

print (f"div_yield_min= {div_yield_min}   div_yield_max= {div_yield_max}")
    
def is_dgr_5yr_high_enough(div_yield, dgr_3yr_5yr):
    dgr_year_checks = [3,5,10,15]
    covered_years = dgr_year_checks[len(dgr_3yr_5yr)-1]
    print(f'ticker: {ticker} dgr_3yr_5yr: {dgr_3yr_5yr}')
    dgr_5yr = dgr_3yr_5yr[5]

    if minimum_years_of_div_increase > covered_years:
        return False

    if (div_yield_min <= div_yield) and (div_yield <= div_yield_max) and (dgr_5yr >= (sweet_total_return - div_yield)):
        return True 
    else:
        return False
    
# tickers = dividend.Symbol.unique()
tickers = ['LMT']

failed_to_process_list = []
structured_data = {}
first_selection = []
# Declaring namedtuple() 
# Stock_data = namedtuple('Stock_data',['symbol','dividend_raw','price', 'dividends_per_year', 'forward_dividend', 'dividend_yield', 'dividend_growth_per_year', 'dgr_3_5_yr']) 

for ticker in tickers:
    current_div_raw = dividend[dividend["Symbol"]==ticker]
    current_div_raw["Datetime"] = pd.to_datetime(current_div_raw['date'])
    current_div_raw = current_div_raw.set_index('Datetime')
    current_price = price[price["Symbol"]==ticker]
    current_split = stock_split[stock_split["Symbol"]==ticker]

    current_divproc = DivProc(ticker, current_div_raw, current_price, current_split)
           
    # print (ticker)
    dividends_per_year = current_divproc.get_dividends_per_year()
    forward_dividend = current_divproc.get_forward_dividend()
    # print(forward_dividend)
    dividend_yield = current_divproc.get_dividend_yield()
    # print(dividend_yield)
    dividend_growth_per_year = current_divproc.get_dividend_growth_per_year()
    # print(dividend_growth_per_year)
    dgr_3_5_yr = current_divproc.get_DGR_3_5yr()
    # print (dgr_3_5_yr)
    
    if ( is_dgr_5yr_high_enough(dividend_yield, dgr_3_5_yr) ):
        first_selection.append( [ticker, dividend_yield, dgr_3_5_yr] )
        print (f"first selection append {ticker}")
        #     structured_data[ticker] = [current_div_raw, dividends_per_year, dividend_yield, dividend_growth_per_year, dgr_3_5_yr]
        #     print (f" ticker {ticker} sp500 div yield {sp500_div_yield}  current div yield {dividend_yield}  dgr_3_5_yr {dgr_3_5_yr}")

    

# for ticker in tickers:   
#     current_div_raw = dividend[dividend["Symbol"]==ticker]
#     current_div_raw["Datetime"] = pd.to_datetime(current_div_raw['date'])
#     current_div_raw = current_div_raw.set_index('Datetime')
#     current_price = price[price["Symbol"]==ticker]
#     current_split = stock_split[stock_split["Symbol"]==ticker]

#     current_divproc = DivProc(ticker, current_div_raw, current_price, current_split) 
#     try:
#         # print (ticker)
#         dividends_per_year = current_divproc.get_dividends_per_year()
#         forward_dividend = current_divproc.get_forward_dividend()
#         # print(forward_dividend)
#         dividend_yield = current_divproc.get_dividend_yield()
#         # print(dividend_yield)
#         dividend_growth_per_year = current_divproc.get_dividend_growth_per_year()
#         # print(dividend_growth_per_year)
#         dgr_3_5_yr = current_divproc.get_DGR_3_5yr()
#         # print (dgr_3_5_yr)
        
#         if ( is_dgr_5yr_high_enough(dividend_yield, dgr_3_5_yr) ):
#             first_selection.append( [ticker, dividend_yield, dgr_3_5_yr] )
#             print (f"first selection append {ticker}")
#             #     structured_data[ticker] = [current_div_raw, dividends_per_year, dividend_yield, dividend_growth_per_year, dgr_3_5_yr]
#             #     print (f" ticker {ticker} sp500 div yield {sp500_div_yield}  current div yield {dividend_yield}  dgr_3_5_yr {dgr_3_5_yr}")

#     except Exception as Argument:  
#         failed_to_process_list.append([ticker, Argument])
#         logger.info(Argument)
     
with open(r'C:\Users\50000700\Python\Python_repos\dividends\excel_files\failed_to_process.csv', 'w', newline='') as failed_file:
    writer = csv.writer(failed_file)
    writer.writerow(["No", "Symbol"])
    for i, symbol in enumerate(failed_to_process_list):
        writer.writerow([i+1, symbol])

with open(r'C:\Users\50000700\Python\Python_repos\dividends\excel_files\first_selection.csv', 'w', newline='') as first_file:
    writer = csv.writer(first_file)
    writer.writerow(["No", "Symbol", "Div_yield", "DGR_5yr"])
    for i, current_item in enumerate(first_selection):
        writer.writerow([i+1, current_item[0], current_item[1], current_item[2]])



# print (len(structured_data))

print (f"overall runtime {time.time() - start_time}")