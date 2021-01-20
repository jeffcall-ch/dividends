from urllib.request import urlopen
import json
import pandas as pd

API_KEY = "606d643d87241cde956b5cd85a3c56d1"
BASE_URL = "https://financialmodelingprep.com/api/v3"
INDEX_PREFIX = "^"
SUPPORTED_INTERVALS = ["1min","5min","15min","30min","1hour","4hour"]
SUPPORTED_CATEGORIES = [
    'profile',
    'quote',
    'quote-short',
    'quotes',
    'search',
    'search-ticker',
    'income-statement',
    'balance-sheet-statement',
    'cash-flow-statement',
    'ratios',
    'enterprise-values',
    'key-metrics',
    'financial-growth',
    'rating',
    'discounted-cash-flow',
    'historical-discounted-cash-flow',
    'stock',
    'earning_calendar',
    'historical',
    'historical-chart',
    'historical-price-full',
    'stock-screener',
    'rss_feed',
    'sp500_constituent',
    'actives',
    'gainers',
    'losers',
    'market-hours',
    'sectors-performance'
]



def get_jsonparsed_data(url):
    """
    Receive the content of ``url``, parse it as JSON and return the object.

    Parameters
    ----------
    url : str

    Returns
    -------
    dict
    """
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)

# url = ("https://financialmodelingprep.com/api/v3/quote/AAPL,FB?apikey=606d643d87241cde956b5cd85a3c56d1")
url = ("https://financialmodelingprep.com/api/v3/quote/AAPL?apikey=606d643d87241cde956b5cd85a3c56d1")

# data = get_jsonparsed_data(url)


df = pd.read_json(url)
print(df)