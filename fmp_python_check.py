from fmp_python.fmp import FMP
import os
import pandas as pd
import requests
import collections
import json
from itertools import zip_longest as zip


os.environ["FMP_API_KEY"] = "606d643d87241cde956b5cd85a3c56d1"
fmp = FMP()

# df = fmp.get_cash_flow_statement('ABT')
# df = fmp.get_data_from_api('ABT', 'income-statement')
# df = fmp.get_data_from_api('ABT', 'historical-price-full/stock_dividend')

# response = fmp.get_dividends('ABT', 'historical-price-full/stock_dividend')
# response = requests.get('https://financialmodelingprep.com/api/v3/historical-price-full/stock_dividend/ABM,ADM,ADP,AFL?apikey=606d643d87241cde956b5cd85a3c56d1')
response = requests.get('https://financialmodelingprep.com/api/v3/historical-price-full/stock_dividend/KO,ABM?apikey=606d643d87241cde956b5cd85a3c56d1')
response_text = response.text


response_text3 = """
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
"""


response_text_2 = """
{
  "historicalStockList" : [ {
    "symbol" : "AFL",
    "historical" : [ {
      "date" : "2020-11-17",
      "label" : "November 17, 20",
      "adjDividend" : 0.2800000000,
      "dividend" : 0.28,
      "recordDate" : "2020-11-18",
      "paymentDate" : "2020-12-1",
      "declarationDate" : "2020-10-27"
    }, {
      "date" : "2020-08-18",
      "label" : "August 18, 20",
      "adjDividend" : 0.2800000000,
      "dividend" : 0.28,
      "recordDate" : "2020-08-19",
      "paymentDate" : "2020-09-01",
      "declarationDate" : "2020-07-28"
    }, {
      "date" : "2020-05-19",
      "label" : "May 19, 20",
      "adjDividend" : 0.2800000000,
      "dividend" : 0.28,
      "recordDate" : "2020-05-20",
      "paymentDate" : "2020-06-01",
      "declarationDate" : "2020-04-29"
    } ]
  }, {
    "symbol" : "ADM",
    "historical" : [ {
      "date" : "2021-02-08",
      "label" : "February 08, 21",
      "adjDividend" : 0.3700000000,
      "dividend" : 0.37,
      "recordDate" : "2021-02-09",
      "paymentDate" : "2021-03-02",
      "declarationDate" : "2021-01-26"
    }, {
      "date" : "2020-11-18",
      "label" : "November 18, 20",
      "adjDividend" : 0.3600000000,
      "dividend" : 0.36,
      "recordDate" : "2020-11-19",
      "paymentDate" : "2020-12-10",
      "declarationDate" : "2020-11-5"
    }, {
      "date" : "2020-08-18",
      "label" : "August 18, 20",
      "adjDividend" : 0.3600000000,
      "dividend" : 0.36,
      "recordDate" : "2020-08-19",
      "paymentDate" : "2020-09-09",
      "declarationDate" : "2020-08-05"
    } ]
  }, {
    "symbol" : "ABM",
    "historical" : [ {
      "date" : "2021-01-06",
      "label" : "January 06, 21",
      "adjDividend" : 0.1900000000,
      "dividend" : 0.19,
      "recordDate" : "2021-1-7",
      "paymentDate" : "2021-2-1",
      "declarationDate" : "2020-12-16"
    }, {
      "date" : "2020-09-30",
      "label" : "September 30, 20",
      "adjDividend" : 0.1850000000,
      "dividend" : 0.185,
      "recordDate" : "2020-10-01",
      "paymentDate" : "2020-11-02",
      "declarationDate" : "2020-09-08"
    }, {
      "date" : "2020-07-01",
      "label" : "July 01, 20",
      "adjDividend" : 0.1850000000,
      "dividend" : 0.185,
      "recordDate" : "2020-07-02",
      "paymentDate" : "2020-08-03",
      "declarationDate" : "2020-06-17"
    }, {
      "date" : "2020-04-01",
      "label" : "April 01, 20",
      "adjDividend" : 0.1850000000,
      "dividend" : 0.185,
      "recordDate" : "2020-04-02",
      "paymentDate" : "2020-05-04",
      "declarationDate" : "2020-03-04"
    } ]
  }, {
    "symbol" : "ADP",
    "historical" : [ {
      "date" : "2020-12-10",
      "label" : "December 10, 20",
      "adjDividend" : 0.9300000000,
      "dividend" : 0.93,
      "recordDate" : "2020-12-11",
      "paymentDate" : "2021-1-1",
      "declarationDate" : "2020-11-11"
    }, {
      "date" : "2020-09-10",
      "label" : "September 10, 20",
      "adjDividend" : 0.9100000000,
      "dividend" : 0.91,
      "recordDate" : "2020-09-11",
      "paymentDate" : "2020-10-01",
      "declarationDate" : "2020-08-05"
    }, {
      "date" : "2020-06-11",
      "label" : "June 11, 20",
      "adjDividend" : 0.9100000000,
      "dividend" : 0.91,
      "recordDate" : "2020-06-12",
      "paymentDate" : "2020-07-01",
      "declarationDate" : "2020-04-08"
    } ]
  } ]
}
"""
# !!! Working code to process 5x tickers per dividend request.
# the problem is, that only 20 rows are served by the server per ticker. Therefore can be forgotten.

words = response_text.split(" ")
# print(words)


def find_all_substring_in_list_of_words(substring, inputs):
  found_list = []
  for i, input in enumerate(inputs):
    if substring in input:
      found_list.append(i)
  return found_list

# find all indexes where the pre_symbol_stopper substrings are located at
pre_symbol_stopper = find_all_substring_in_list_of_words('"symbol"', words)
# add 2 to all index locations, which will give back the exact indexes of the symbols
symbol_index_list = [x+2 for x in pre_symbol_stopper]
# remove " characters and strip to get pure symbols
symbol_list = [words[x][1:-3].strip() for x in symbol_index_list]

print (f"symbol list {symbol_list}")



json_starter_index_list = find_all_substring_in_list_of_words("[",words)
json_stopper_index_list = find_all_substring_in_list_of_words("]",words)

# if there are more, than one symbols requested. This means that the json starter index list has more elements, than 1
if len(json_starter_index_list) > 1:
  # pop first starter as it is before all symbols in the json. We don't need it
  # pop last item from stopper list as it is the complete json closer, not a symbol closer
  json_starter_index_list.pop(0)
  json_stopper_index_list.pop(-1)


# print (f"symbol indexes {symbol_index_list}")
# print (f"json starter indexes {json_starter_index_list}")
# print (f"json stopper indexes {json_stopper_index_list}")

# add one to all list items to get real start of payload
payload_starter_index_list = [x+1 for x in json_starter_index_list]
# payload stopper remains the same as json_stopper_index_list
payload_stopper_index_list = json_stopper_index_list


def create_separate_json_strings():
  payload_list = []
  for i, starter in enumerate(payload_starter_index_list):
    stopper = payload_stopper_index_list[i]
    current_json = ' '.join(words[starter:stopper])
    current_json.strip()
    current_json.rstrip('\r\n')
    current_json.lstrip('\r\n')
    # print (current_json)
    current_json = '[' + current_json + ']'
    payload_stopper_index_list.append(current_json)
    payload_list.append(current_json)
  return payload_list


separate_json_strings = create_separate_json_strings()
# print(separate_json_strings)

div_frame_list = []

for i, json_string in enumerate(separate_json_strings):
  # print (json_string)
  formatted_json = json.loads(json_string)
  current_dividend = pd.DataFrame(formatted_json)
  current_dividend["Symbol"] = symbol_list[i]
  print(current_dividend)
  div_frame_list.append(current_dividend)

if len(div_frame_list) > 1:
  dividends = pd.concat(div_frame_list)
else:
  dividends = div_frame_list[0]

print ("FINAL PANDAS FRAME")
print (dividends.shape)
print (dividends)






# print (symbols_list)



# for items in zip(payload_starter_index_list, payload_stopper_index_list):
#     for item in items:
#       print (item)



# symbols_list = []

# for i, word in enumerate(words):
#   if word == '"symbol"':
#     print (i)
#     symbol_indexes.append(i+2)

# for symbol in symbol_indexes:
#   symbol_text = words[symbol][1:-3].strip()
#   symbols_list.append(symbol_text)
#   print (symbol_text)

#  ORIGINAL CODE
# response_text = response.text
# starter_char = response_text.find(" [ ")
# end_char = response_text.find(" ]")

# formatted_text = response_text[(starter_char):(end_char+2)].strip()
# formatted_text.rstrip('\r\n')
# formatted_text.lstrip('\r\n')
# print (formatted_text)

# formatted_json = json.loads(formatted_text)
# print (formatted_json)
# df = pd.DataFrame(formatted_json)

# print(df)
