import pandas as pd
from datetime import datetime

file_names = [r'\dividend.csv', r'\cashflow.csv', r'\income.csv', r'\price.csv']

dividend = pd.read_csv(r'C:\Users\50000700\Python\Python_repos\dividends\excel_files' + file_names[0])
cashflow = pd.read_csv(r'C:\Users\50000700\Python\Python_repos\dividends\excel_files' + file_names[1])
income = pd.read_csv(r'C:\Users\50000700\Python\Python_repos\dividends\excel_files' + file_names[2])
price = pd.read_csv(r'C:\Users\50000700\Python\Python_repos\dividends\excel_files' + file_names[3])

dataframes = [dividend, cashflow, income, price]

for dataframe in dataframes:
    print (dataframe.shape)
    print (dataframe)

# for i, dataframe in enumerate(dataframes):
#     input_path = r'C:\Users\50000700\Python\Python_repos\dividends\excel_files' + file_names[i]
#     print (input_path)
#     current_dataframe = pd.read_csv(input_path)
#     dataframe = current_dataframe
