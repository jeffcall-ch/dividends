import requests
import datetime
from dateutil.parser import parse as parsedate
import pathlib
import os
import shutil
import pandas as pd

# path definitions
python_repo_home_folder = pathlib.Path.home() / "Python" / "Python_repos" / "dividends"
dripinvesting_folder = python_repo_home_folder / "excel_files" / "dripinvesting"

# url and proxies definition
url = "https://bit.ly/USDividendChampions1"
proxies = {
    'http' : 'proxy.threatpulse.net:8080',
    'https' : 'proxy.threatpulse.net:8080',
}

# get the time from response
response = requests.get(url, proxies=proxies)
url_time = response.headers['last-modified']
url_date = parsedate(url_time)

# create filename with exact date from url_date
dripinvesting_filename = 'dividend_champions url_date_' + str(url_date)[:-15] + '.xls'
dripinvesting_filepath = dripinvesting_folder / dripinvesting_filename

# create a list of files in the dripinvesting folder
def getListOfFiles(dirName):
    listOfFile = os.listdir(dirName)
    allFiles = list()
    for entry in listOfFile:
        fullPath = os.path.join(dirName, entry)
        if os.path.isfile(fullPath):
            allFiles.append(fullPath)       
    return allFiles     
listOfFiles = getListOfFiles(dripinvesting_folder.as_posix())

# if there is only 1 xls file in the dividends folder AND the url_date is newer, than the file_date
# then download new file
file_time_of_latest_downloaded_xls = datetime.datetime.fromtimestamp(os.path.getmtime(listOfFiles[0])).astimezone()
if (len(listOfFiles) == 1 & (url_date > file_time_of_latest_downloaded_xls)):
    # move obsolete file to the "obsolete folder"
    path_of_file = pathlib.Path(listOfFiles[0])
    destination_path_of_file = path_of_file.parent / "obsolete" / path_of_file.name
    shutil.move(path_of_file, destination_path_of_file)

    # donwload new file
    with open(dripinvesting_filepath.as_posix(), 'wb') as output:
        output.write(response.content)
else:
    print("New dripinvesting file downloaded.")
    print("url_date:" + str(url_date))
    print("file_time: " + str(file_time_of_latest_downloaded_xls))


