import pathlib
import logging
import os
import datetime

python_repo_home_folder = pathlib.Path.home() / "Python" / "Python_repos" / "dividends"
dripinvesting_folder = python_repo_home_folder / "excel_files" / "dripinvesting"

# print(dripinvesting_filepath.as_posix())

def getListOfFiles(dirName):
    listOfFile = os.listdir(dirName)
    allFiles = list()
    for entry in listOfFile:
        fullPath = os.path.join(dirName, entry)
        if os.path.isfile(fullPath):
            allFiles.append(fullPath)       
    return allFiles     
    
listOfFiles = getListOfFiles(dripinvesting_folder.as_posix())

if len(listOfFiles) == 1:
    file_time = datetime.datetime.fromtimestamp(os.path.getmtime(listOfFiles[0]))
    print(str(file_time))


for elem in listOfFiles:
    print(elem)