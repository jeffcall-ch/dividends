import pandas as pd
import requests
import os
import io
from datetime import datetime
import json
import aiohttp
import asyncio 

from fmp_python.common.constants import BASE_URL,INDEX_PREFIX
from fmp_python.common.requestbuilder import RequestBuilder
from fmp_python.common.fmpdecorator import FMPDecorator
from fmp_python.common.fmpvalidator import FMPValidator
from fmp_python.common.fmpexception import FMPException


   
"""
Base class that implements api calls 
"""

class FMP(object):
  

    def __init__(self, session, api_key=None, output_format='pandas', write_to_file=False):
        self.api_key = api_key or os.getenv('FMP_API_KEY')
        self.output_format = output_format
        self.write_to_file = write_to_file
        self.current_day = datetime.today().strftime('%Y-%m-%d')
        self.session = session
        
   

    async def get_dividends_and_stock_splits(self, symbol, reportType):
        rb = RequestBuilder()
        rb.set_category(reportType)
        rb.add_sub_category(symbol)
        quote = await self.__do_request__(rb.compile_request())

        response_text = await quote.text()
        starter_char = response_text.find(" [ ")
        end_char = response_text.find(" ]")

        formatted_text = response_text[(starter_char):(end_char+2)].strip()
        formatted_text.rstrip('\r\n')
        formatted_text.lstrip('\r\n')
        # print (formatted_text)

        formatted_json = json.loads(formatted_text)
        df = pd.DataFrame(formatted_json)
        return df
    
        
    @FMPDecorator.write_to_file
    @FMPDecorator.format_data
    def get_data_from_api(self, symbol, reportType):
        rb = RequestBuilder()
        rb.set_category(reportType)
        rb.add_sub_category(symbol)
        quote = self.__do_request__(rb.compile_request())
        return quote
    
    @FMPDecorator.write_to_file
    @FMPDecorator.format_data
    def get_cash_flow_statement(self, symbol):
        rb = RequestBuilder()
        rb.set_category('cash-flow-statement')
        rb.add_sub_category(symbol)
        quote = self.__do_request__(rb.compile_request())
        return quote

    @FMPDecorator.write_to_file
    @FMPDecorator.format_data
    def get_quote_short(self, symbol):
        rb = RequestBuilder()
        rb.set_category('quote-short')
        rb.add_sub_category(symbol)
        quote = self.__do_request__(rb.compile_request())
        return quote
    
    @FMPDecorator.write_to_file
    @FMPDecorator.format_data
    def get_quote(self,symbol):
        rb = RequestBuilder()
        rb.set_category('quote')
        rb.add_sub_category(symbol)
        quote = self.__do_request__(rb.compile_request())
        return quote

    def get_index_quote(self,symbol):
        return FMP.get_quote(self,str(INDEX_PREFIX)+symbol)
    
    @FMPDecorator.write_to_file
    @FMPDecorator.format_data
    def get_historical_chart(self, interval, symbol):
        if FMPValidator.is_valid_interval(interval):
            rb = RequestBuilder()
            rb.set_category('historical-chart')
            rb.add_sub_category(interval)
            rb.add_sub_category(symbol)
            hc = self.__do_request__(rb.compile_request())
            return hc
        else:
            raise FMPException('Interval value is not valid',FMP.get_historical_chart.__name__)

    def get_historical_chart_index(self,interval,symbol):
        return FMP.get_historical_chart(self, interval, str(INDEX_PREFIX)+symbol)

    @FMPDecorator.write_to_file
    @FMPDecorator.format_historical_data
    def get_historical_price(self,symbol):
        rb = RequestBuilder()
        rb.set_category('historical-price-full')
        rb.add_sub_category(symbol)
        hp = self.__do_request__(rb.compile_request())
        return hp

    async def __do_request__(self,url):
        # print (self.session.request(method="GET", url=url))
        response = await self.session.get(url)
        print (response.status)
        return response
