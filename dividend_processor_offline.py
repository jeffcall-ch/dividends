from fmp_python.fmp import FMP
import os
import pandas as pd
from datetime import datetime
from SP500_div_yield_crawler import SP500
import numpy as np
import time


class DividendProcessor(object):
    def __init__(self, ticker, dividends_raw, real_time_price, stock_split):
        self.ticker = ticker.upper()
        self.today = datetime.today()
        self.this_year = self.today.year
        self.dividends_raw = dividends_raw
        self.real_time_price = real_time_price
        self.stock_split = stock_split

    # def get_dividends_raw(self):
    #     # dividend, date  - historical dividend values and dates
    #     self.dividends_raw = self.fmp.get_dividends(self.ticker, 'historical-price-full/stock_dividend')

    #     # set proper DateTime object as the index of the dataframe
    #     self.dividends_raw['Datetime'] = pd.to_datetime(self.dividends_raw['date'])

    #     try:
    #         # find days difference between rows. Needed to see data gap (for instane AAPL dividends)
    #         self.dividends_raw['Datetime_DaysDiffRows']=self.dividends_raw['Datetime'].diff().dt.days
    #         # find if there is more than 365 days passed between rows. If that happens, delete all rows below
    #         index_of_first_gap = np.where(self.dividends_raw['Datetime_DaysDiffRows'].lt(-400))[0][0]
    #         self.dividends_raw = self.dividends_raw.iloc[:index_of_first_gap]
    #     except: 
    #         # no gaps found in datetime
    #         pass
        
    #     self.dividends_raw = self.dividends_raw.set_index('Datetime')
    #     self.dividends_raw["Symbol"] = self.ticker
    #     # export to csv. Use header only for the first time, then only append new rows
    #     # output_path = r'C:\Users\50000700\Python\Python_repos\dividends\excel_files\dividends_raw.csv'
    #     # self.dividends_raw.to_csv(output_path, mode='a', header=not os.path.exists(output_path))
    #     print (self.dividends_raw)
    #     return self.dividends_raw   

    # def get_real_time_price(self):
    #     self.real_time_price = self.fmp.get_quote_short(self.ticker)
    #     print (f"REAL TIME PRICE {self.real_time_price}")
    #     return self.real_time_price

    def get_split_corrigated_dividends(self):
        if self.stock_split.empty:
            return self.dividends_raw
        else:
            # create nre column with copy
            self.dividends_raw['dividend_split_corrigated'] = self.dividends_raw['dividend'].copy()
            for split_date in self.stock_split.index.tolist():
                print (split_date)
                numerator = self.stock_split.loc[self.stock_split.index==split_date, 'numerator'].values[0]
                denominator = self.stock_split.loc[self.stock_split.index==split_date, 'denominator'].values[0]
                ratio = numerator / denominator
                print (f"split date {split_date} numerator {numerator} denominator {denominator}")

                self.dividends_raw.loc[self.dividends_raw.index >= split_date, 'dividend_split_corrigated'] = self.dividends_raw['dividend_split_corrigated'] * ratio
            return self.dividends_raw

    def get_dividends_per_year(self):
        # resample annually and sum dividend values. Note that year end (Dec 31) will be shown for all groups
        dividends_per_year = self.dividends_raw.resample("A")["adjDividend"].sum()
        return dividends_per_year

    def get_dividend_frequency_of_prev_year(self):
        # calculates the last year's dividend frequency and returns how many times it was paid
        dividends = self.dividends_raw.resample("A")["date"].count()
        mask = (dividends.index > (str(self.this_year-1)+'-01-01')) & (dividends.index <= (str(self.this_year-1)+'-12-31'))
        dividends_filtered=dividends.loc[mask]
        return dividends_filtered.iloc[0]

    def get_dividend_frequency_all_years(self):
        dividends_freq_filtered = self.dividends_raw.resample("A")["date"].count()
        years_list = dividends_freq_filtered.index.year.tolist()
        print (years_list)
        freq_list = self.dividends_raw.resample("A")["date"].count().tolist()
        print (freq_list)
        frequencies = {}
        for i in range(1,16):
            frequencies[i] = []
        for i, year in enumerate(years_list):
            frequencies[freq_list[i]].append(year)
        print (frequencies)



        

        # indexes = dividends_freq_filtered["date"].tolist()
        # print (indexes)

        return dividends_freq_filtered

    def get_dividend_dates_values_of_year(self, year):
        mask = (self.dividends_raw.index > (str(year)+'-01-01')) & (self.dividends_raw.index <= (str(year)+'-12-31'))
        dividends_filtered=self.dividends_raw.loc[mask]
        return dividends_filtered

    def get_dividend_months_of_year(self, year):
        mask = (self.dividends_raw.index > (str(year)+'-01-01')) & (self.dividends_raw.index <= (str(year)+'-12-31'))
        dividends_filtered_of_year=self.dividends_raw.loc[mask]
        list_of_div_months = dividends_filtered_of_year.index.tolist()
        list_of_div_months = [date.strftime("%m") for date in list_of_div_months]
        return list_of_div_months

    def is_div_frequency_same_for_years(self, new_year, old_year):
        # if no dividends paid - early in the year return same frequency as old year
        if len(self.get_dividend_months_of_year(new_year))==0:
            return True
        if all(elem in self.get_dividend_months_of_year(old_year)  for elem in self.get_dividend_months_of_year(new_year)):
            return True
        else:
            # print (f"Dividend frequency of ticker: {self.ticker} for years {new_year} and {old_year} don't match. Further calculation is not possible!")
            raise ValueError(f"Dividend frequency of ticker {self.ticker} for years {new_year} and {old_year} don't match. Further calculation is not possible!")

    def get_forward_dividend(self):
        # take last dividend paid and multiply it with the dividend payment frequency
        last_dividend = self.dividends_raw.iloc[0]["adjDividend"]
        if self.is_div_frequency_same_for_years(self.this_year, self.this_year-1):
            return (last_dividend * self.get_dividend_frequency_of_prev_year())
        else:
            raise ValueError(f"Dividend frequency of ticker {self.ticker} for years {self.this_year} and {self.this_year-1} don't match. Further calculation is not possible!")
        
    def get_dividend_yield(self):
        # returns dividend yield in %
        try: 
            return (self.get_forward_dividend() / self.real_time_price.iloc[0]["price"] * 100)
        except:
            print (f"No real time price data is available from API: {self.ticker}")
            return -1

    def get_dividend_growth_per_year(self):
        # get dividend growth per year
        dividend_gr_per_yr = pd.DataFrame()
        # remove current year line as it cannot be complete and we are interested in historical data
        if self.stock_split.empty:
            dividend_gr_per_yr['yearlyDividendValue'] = self.dividends_raw.resample("A")["dividend"].sum()
        else:
            dividend_gr_per_yr['yearlyDividendValue'] = self.dividends_raw.resample("A")["dividend_split_corrigated"].sum()
        
        dividend_gr_per_yr['dividendGrowth'] = dividend_gr_per_yr.pct_change()
        dividend_gr_per_yr = dividend_gr_per_yr.sort_index(ascending=False)

        # mask out row of current year
        mask = (dividend_gr_per_yr.index <= (str(self.this_year-1)+'-12-31'))
        dividend_gr_per_yr_filtered=dividend_gr_per_yr.loc[mask]

        return dividend_gr_per_yr_filtered

    def get_most_recent_dividend_cut_year(self):
        # result is the closest year from today when the dividend was cut last time. From that year he dividends are increasing again
        # if there is a dividend cut, then the yearly dividend growth rate will contain a negative growth for the particular cut year
        div_gr_per_year = self.get_dividend_growth_per_year()
        index = div_gr_per_year.dividendGrowth.lt(0).idxmax()

        # if index is the most recent date of the dataframe (first element), then set it to 1970-1-1 showing, that there was not a single cut in the dividends
        # print (f"first valid index {div_gr_per_year.first_valid_index()}")
        if index == div_gr_per_year.first_valid_index():
            # if there is an unlikely event of the most recent year was a div cut (see ticker ABM), then return this most recent year
            # print (f"first element of div grwth rate {div_gr_per_year.iloc[0][1]}")
            if div_gr_per_year.iloc[0][1] < 0:
                return index
            else:  
                return datetime(1970, 1, 1)
        return index

    def get_DGR_3_5yr(self):
        # calculate DGR1yr, DGR3yr, DGR5yr and potentially DGR10yr
        # note, that CAGR calculation is used. http://www.moneychimp.com/features/cagr.htm
        # give it current dividend, old dividend and number of years
        # calculation gives uniform yearly growth value to reach final dividend
        # note that dripinvesting has mistakes in their input data and they will not always match with this result
        dividend_gr_per_yr = self.get_dividend_growth_per_year()
        years_to_check = [3,5,10,15]
        list_of_DGR = {}
            
        last_dividend_cut_year = self.get_most_recent_dividend_cut_year()
        # print (f"first dividend cut year index from today {last_dividend_cut_year}")
        
        for year in years_to_check:
            # if 3 years dgr to be calculated we need to go back 4 years to start the analsysis. 
            # therefore for the year masking we have to use a corrigated year value to get the correct interval
            year_corrigated = year + 1
            mask = (dividend_gr_per_yr.index > (str(self.this_year-year_corrigated)+'-01-01')) & (dividend_gr_per_yr.index <= (str(self.this_year-1)+'-12-31'))
            dividends_gr_x_yr=dividend_gr_per_yr.loc[mask]
            if len(dividends_gr_x_yr.index) == year_corrigated and last_dividend_cut_year.year < (self.this_year-year_corrigated) :
                div_current = dividends_gr_x_yr.iloc[0]["yearlyDividendValue"]
                div_old = dividends_gr_x_yr.iloc[-1]["yearlyDividendValue"]
                cagr = (((div_current / div_old) ** (1/year)) - 1) * 100
                # print (f"year {year} div_current {div_current} div_old {div_old} cagr {cagr}")
                list_of_DGR[year] = cagr
        return (list_of_DGR)

# # list_of_tickers = ["ADP","ADM", "AFL", "ALB", "AOS", "APD", "AROW"]
# list_of_tickers = ["KO"]

# request_counter = 0
# start_time = time.time()

# for ticker in list_of_tickers:
#     request_start_time = time.time()
#     dataproc = DividendProcessor(ticker)
#     print (ticker)
#     # instantiating a DataProcessor class will make 2 requests
#     # https://financialmodelingprep.com/developer/docs/terms-of-service/ scroll to bottom
#     # 10 requests per second are allowed
#     request_counter += 2
#     if request_counter >= 10 :
#         request_counter = 0
#         print ("reached 10 requests")
#         print("--- %s seconds ---" % (time.time() - start_time))
#         if (time.time() - start_time) < 1 :
#             print ("reached 10 requests waiting 1 second")
#             print("--- %s seconds ---" % (time.time() - start_time))
#             time.sleep(1)
#             start_time = time.time()

#     dataproc.get_dividends_per_year()
#     dataproc.get_dividend_frequency_of_prev_year()
#     dataproc.get_dividend_dates_values_of_year("2020")
#     dataproc.get_dividend_months_of_year(2021)
#     dataproc.get_dividend_months_of_year(2020)
#     dataproc.is_div_frequency_same_for_years(2021, 2020)
#     dataproc.get_forward_dividend()
#     dataproc.get_dividend_yield()
#     dataproc.get_dividend_growth_per_year()
#     dataproc.get_DGR_3_5yr()
#     dataproc.get_most_recent_dividend_cut_year()
#     print (f"dividend request processed in: {time.time()-request_start_time}")


# dataproc = DividendProcessor('KO')
# print (f"dividends per year {dataproc.get_dividends_per_year()}")
# print (f"div freq per year {dataproc.get_dividend_frequency_of_prev_year()}")
# print (f"div dates of 2020 {dataproc.get_dividend_dates_values_of_year(2020)}")
# print (f"div months 2021 {dataproc.get_dividend_months_of_year(2021)}")
# print (f"div months 2020 {dataproc.get_dividend_months_of_year(2020)}")
# print (f"is freq same for 2021 and 2020 {dataproc.is_div_frequency_same_for_years(2021, 2020)}")
# print (f"forward dividend {dataproc.get_forward_dividend()}")
# print (f"dividend yield {dataproc.get_dividend_yield()}")
# print (f"div growth per year {dataproc.get_dividend_growth_per_year()}")
# print (f"DGR 3yr 5yr {dataproc.get_DGR_3_5yr()}")
# print (f"most recent div cut year {dataproc.get_most_recent_dividend_cut_year()}")

  