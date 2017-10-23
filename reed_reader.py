#!/usr/bin/env python3

#All the imports
from pyprind import ProgBar as pb
import time
import requests
import json
from pandas.io.json import json_normalize
import pandas as pd
from easygui import *


#Here I choose what to get from Reed.co.uk database.
msg = "Introduce the data to search or use the defaults"
title = "Vacancies Selection"
fieldNames = ["Location", "Distance", "Keywords"]
fieldValues = ["W38EL", "1","developer"]
fieldValues = multenterbox(msg, title, fieldNames, fieldValues)

while 1:
    if fieldValues == None: break
    errmsg = ""
    #The reason to be len -1 is to avoid checking keywords as you might search without any keyword. 
    for i in range(len(fieldNames)-1):
      if fieldValues[i].strip() == "":
        errmsg = errmsg + ('"%s" is a required field.\n\n' % fieldNames[i])
    if errmsg == "": break # no problems found
    fieldValues = multenterbox(errmsg, title, fieldNames, fieldValues)


locationName = fieldValues[0]
distance = fieldValues[1]
keywords = fieldValues[2]

#Aditional values for a future
permanent = ""
temp = ""
partTime = ""
fullTime = ""
minimumSalary = ""
maximumSalary = ""
perHour = ""
postedByRecruitmentAgency =""
postedByDirectEmployer = ""
graduate = ""


prefixurl = "http://www.reed.co.uk/api/1.0/search?keywords=" + keywords + "&locationName=" + locationName + "&distancefromlocation= " + str(distance) + "&resultsToTake=100"


response = requests.get(prefixurl,
             auth=('3f4426b0-a18b-460a-b0d8-0937cf861f72', ''))

data = json.loads(response.text)
total = data['totalResults']
pages = total // 100

if (ynbox('There are a total of ' + str(total) + ' vacancies matching. It will take ' + str(pages) + ' seconds to download them all', 'Shall I continue or Piss Off', ('Continue','Piss Off'))) == 1:
    print("Downloading")
else:
    print("You have selected to cancel the program will now terminate")
    time.sleep(2)
    exit()
    
bar = pb(pages, monitor=True, bar_char='#')
for x in range(0,pages+1):
    url = prefixurl + "&resultsToSkip=" + str(x*100)
    response = requests.get(url,auth=('3f4426b0-a18b-460a-b0d8-0937cf861f72', ''))
    time.sleep(0.2)
    bar.update()
    data = json.loads(response.text)
    tempdf = json_normalize(data, 'results')
    if x == 0:
        finaldf = tempdf
    else:
        finaldf = pd.concat([finaldf, tempdf])


print("DDBB fully downloaded. Choose now a file to save it")



#Filters
finaldf = finaldf[(finaldf.currency=='None')  | (finaldf.currency=='GBP')]
finaldf = finaldf[(finaldf.employerName!='Just IT Recruitment') & (finaldf.employerName!='Just IT Recruitment')]   
finaldf = finaldf[~finaldf["jobTitle"].str.contains("Apprentice")]
finaldf = finaldf[~finaldf["jobTitle"].str.contains("Sales")]
#finaldf = finaldf[(finaldf["jobTitle"].str.contains("Developer")) | (finaldf["jobTitle"].str.contains("Engineer"))]

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
