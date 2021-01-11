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
df = pd.read_excel(listOfFiles[0], sheet_name='All CCC')

# drop first 4 rows
df = df.drop(df.index[0:3])
print(df)