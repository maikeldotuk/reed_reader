#!/usr/bin/env python3

#All the imports
from pyprind import ProgBar as pb
import time
import requests
import json
from pandas.io.json import json_normalize
import pandas as pd
from easygui import *
import grequests
import datetime

MAX_CONNECTIONS = 100
fieldValues = ["W38EL", "10","developer"]


locationName = fieldValues[0]
distance = fieldValues[1]
keywords = fieldValues[2]
prefixurl = "http://www.reed.co.uk/api/1.0/search?keywords=" + keywords + "&locationName=" + locationName + "&distancefromlocation= " + str(distance) + "&resultsToTake=100"


response = requests.get(prefixurl,
             auth=('3f4426b0-a18b-460a-b0d8-0937cf861f72', ''))
data = response.json()
total = data['totalResults']
pages = total // 100
finaldf = json_normalize(data, 'results')




time1 = datetime.datetime.now()


urlsList = []
for x in range(1, pages+1):
    urlsList.append(prefixurl + "&resultsToSkip=" + str(x*100))


results = []
for x in range(1, pages+1, MAX_CONNECTIONS):
    rs = (grequests.get(u,auth=('3f4426b0-a18b-460a-b0d8-0937cf861f72', '')) for u in urlsList[x:x+MAX_CONNECTIONS])
#    time.sleep(0.2)
    results.extend(grequests.map(rs))
    print("Waiting")





time2 = datetime.datetime.now()

difference = time2 - time1
print("Difference = ", difference.seconds, " in seconds")






newBar = pb(len(urlsList), monitor=True, bar_char='#')
for element in results:
    data = element.json()
    finaldf = pd.concat([finaldf, json_normalize(data, 'results')])
    newBar.update()



#Filters
finaldf = finaldf[(finaldf.currency=='None')  | (finaldf.currency=='GBP')]
finaldf = finaldf[(finaldf.employerName!='Just IT Recruitment') & (finaldf.employerName!='Just IT Recruitment')]   
finaldf = finaldf[~finaldf["jobTitle"].str.contains("Apprentice")]
finaldf = finaldf[~finaldf["jobTitle"].str.contains("Sales")]
finaldf = finaldf[(finaldf["jobTitle"].str.contains("Developer")) | (finaldf["jobTitle"].str.contains("Engineer"))]


#Cleaning up
anotherdf = finaldf[['jobId','date', 'jobTitle', 'employerId', 'employerName','applications', 'expirationDate', 'jobDescription','jobUrl', 'locationName','maximumSalary','minimumSalary'  ]]
anotherdf.set_index('jobId', inplace=True)


#Here I've added a file selector to choose the name of the excel spreadsheet and where it'll be saved. 
letMeChose = filesavebox("Choose a folder","Reedcouk", "reed",[" *.xlsx"]) 
if letMeChose!=None:
    letMeChose+=".xlsx"
    writer = pd.ExcelWriter(letMeChose, engine='openpyxl')
    anotherdf.to_excel(writer,'Vacancies')
    writer.save()
else:
    print("No folder selected. The program will now close")
    time.sleep(2)

