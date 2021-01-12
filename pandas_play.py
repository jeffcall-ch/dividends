import pathlib
import pandas as pd
import os


python_repo_home_folder = pathlib.Path.home() / "Python" / "Python_repos" / "dividends"
dripinvesting_folder = python_repo_home_folder / "excel_files" / "dripinvesting"

def getListOfFiles(dirName):
    listOfFile = os.listdir(dirName)
    allFiles = list()
    for entry in listOfFile:
        fullPath = os.path.join(dirName, entry)
        if os.path.isfile(fullPath):
            allFiles.append(fullPath)       
    return allFiles     

# import latest dripinvesting excel file into pandas
listOfFiles = getListOfFiles(dripinvesting_folder.as_posix())

# read the excel file
# combine rows 4-5 to be the header. By doing this the real pandas df will start from the header (and you don't need to drop rows..)
# note that in case the top cell is empty, then it will use the closest top cell value to the left.
# EXAMPLE: "TickerSymbol" column (col "B" in excel) name is correct. But the next column is empty top cell and "Sector" bottom cell (col "C" in excel). 
#           Now it will be "TickerSector"
df = pd.read_excel(listOfFiles[0], sheet_name='All CCC', header=[4,5])

# flatten the multi index header: https://stackoverflow.com/questions/41931332/how-do-i-flatten-a-hierarchical-column-index-in-a-pandas-dataframe
df.columns = df.columns.map(lambda x: ''.join([*map(str, x)]))

# drop last rows of summary where not individual companies are shown but sector performance
df = df.dropna(subset=['TickerSector'])

# select only rows where DGR is not showing a decreasing trend
df = df[(df['DGR1-yr']>=df['DGR3-yr']) & (df['DGR3-yr']>=df['DGR5-yr']) & (df['DGR5-yr']>=df['DGR10-yr'])]


print(df)