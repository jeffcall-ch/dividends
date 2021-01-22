from fmp_python.fmp import FMP
import os
import pandas as pd
import requests
import collections
import json


os.environ["FMP_API_KEY"] = "606d643d87241cde956b5cd85a3c56d1"
fmp = FMP()

# df = fmp.get_cash_flow_statement('ABT')
# df = fmp.get_data_from_api('ABT', 'income-statement')
# df = fmp.get_data_from_api('ABT', 'historical-price-full/stock_dividend')

response = fmp.get_dividends('ABT', 'historical-price-full/stock_dividend')

""" response_text = """
{
  "symbol" : "ABT",
  "historical" : [ {
    "date" : "2021-01-14",
    "label" : "January 14, 21",
    "adjDividend" : 0.4500000000,
    "dividend" : 0.45,
    "recordDate" : "2021-1-15",
    "paymentDate" : "2021-2-16",
    "declarationDate" : "2020-12-11"
  }, {
    "date" : "2020-10-14",
    "label" : "October 14, 20",
    "adjDividend" : 0.3600000000,
    "recordDate" : "",
    "paymentDate" : "",
    "declarationDate" : ""
  }, {
    "date" : "1983-01-11",
    "label" : "January 11, 83",
    "adjDividend" : 0.0058900000,
    "recordDate" : "",
    "paymentDate" : "",
    "declarationDate" : ""
  } ]
}
""" """
response_text = response.text
starter_char = response_text.find(" [ ")
end_char = response_text.find(" ]")

formatted_text = response_text[(starter_char):(end_char+2)].strip()
formatted_text.rstrip('\r\n')
formatted_text.lstrip('\r\n')
print (formatted_text)

formatted_json = json.loads(formatted_text)
print (formatted_json)
df = pd.DataFrame(formatted_json)

print(df)