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
df = pd.read_excel(listOfFiles[0], sheet_name='All CCC', header=[4,5]) 

# drop last rows of summary where not individual companies are shown but sector performance
df = df.dropna(subset=['Sector'])

# list(df.columns.values)

# print(df.columns.tolist())


print(df)