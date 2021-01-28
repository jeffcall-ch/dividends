from fmp_python.fmp import FMP
import os
import pandas as pd
from datetime import datetime
from SP500_div_yield_crawler import SP500


class DataProcessor(object):
    def __init__(self, ticker):
        self.ticker = ticker.upper()
        os.environ["FMP_API_KEY"] = "606d643d87241cde956b5cd85a3c56d1"
        self.fmp = FMP()
        self.today = datetime.today()
        self.this_year = self.today.year
        self.dividends_raw = self.get_dividends_raw()
        self.real_time_price = self.get_real_time_price()

    def get_dividends_raw(self):
        # dividend, date  - historical dividend values and dates
        self.dividends_raw = self.fmp.get_dividends(self.ticker, 'historical-price-full/stock_dividend')

        # set proper DateTime object as the index of the dataframe
        self.dividends_raw['Datetime'] = pd.to_datetime(self.dividends_raw['date'])
        self.dividends_raw = self.dividends_raw.set_index('Datetime')
        return self.dividends_raw   

    def get_real_time_price(self):
        self.real_time_price = self.fmp.get_quote_short(self.ticker)
        return self.real_time_price

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
        return (self.get_forward_dividend() / self.real_time_price.iloc[0]["price"] * 100)

    def get_dividend_growth_per_year(self):
        pass



dataproc = DataProcessor('AAPL')
# print (dataproc.get_dividends_per_year())
# print (dataproc.get_dividend_frequency_of_prev_year())
# print (dataproc.get_dividend_dates_values_of_year("2020"))
print (dataproc.get_dividend_months_of_year(2021))
print (dataproc.get_dividend_months_of_year(2020))
print (dataproc.is_div_frequency_same_for_years(2021, 2020))
print (dataproc.get_forward_dividend())
print (dataproc.get_dividend_yield())



    