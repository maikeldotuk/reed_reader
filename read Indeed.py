#!/usr/bin/env python3

from pyprind import ProgBar as pb
import requests
import json
from pandas.io.json import json_normalize
import pandas as pd
import xml.etree.ElementTree as ET
import xmltodict
from easygui import *
import time

#Here I choose what to get from Indeed.com database.
msg = "Introduce the data to search or use the defaults"
title = "Vacancies Selection"
fieldNames = ["Location", "Distance", "Keywords"]
fieldValues = ["W38EL", "10","developer"]
fieldValues = multenterbox(msg, title, fieldNames, fieldValues)

while 1:
    if fieldValues == None: break
    errmsg = ""
    for i in range(len(fieldNames)):
      if fieldValues[i].strip() == "":
        errmsg = errmsg + ('"%s" is a required field.\n\n' % fieldNames[i])
    if errmsg == "": break # no problems found
    fieldValues = multenterbox(errmsg, title, fieldNames, fieldValues)


locationName = fieldValues[0]
distance = fieldValues[1]
keywords = fieldValues[2]

prefixurl = "http://api.indeed.com/ads/apisearch?publisher=5190564009051576&q=" + keywords + "&l=" + locationName + "&co=GB&radius=" + str(distance) + "&v=2&limit=25"

response = requests.get(prefixurl)

shit = xmltodict.parse(response.text)
jsonShit = json.dumps(shit)
jsonShit
data = json.loads(jsonShit)

total = data['response']['totalresults']
data = data['response']['results']
pages = int(total) // 25



if (ynbox('There are a total of ' + str(total) + ' vacancies matching. It will take ' + str(pages) + ' seconds to download them all', 'Shall I continue or Piss Off', ('Continue','Piss Off'))) == 1:
    print("Downloading")
else:
    print("You have selected to cancel the program will now terminate")
    time.sleep(2)
    exit()

bar = pb(pages, monitor=True, bar_char='#')
for x in range(0,pages+1):
    url = prefixurl + "&start=" + str(x*25)
    response = requests.get(url)
    time.sleep(0.2)
    bar.update()
    shit = xmltodict.parse(response.text)
    jsonShit = json.dumps(shit)
    jsonShit
    data = json.loads(jsonShit)
    data = data['response']['results']
    tempdf = json_normalize(data, 'result')

    if x == 0:
        finaldf = tempdf
    else:
        finaldf = pd.concat([finaldf, tempdf])


print("DDBB fully downloaded. Choose now a file to save it")
#Filters

finaldf = finaldf[~finaldf["jobtitle"].str.contains("Apprentice")]
finaldf = finaldf[~finaldf["jobtitle"].str.contains("Sales")]
finaldf = finaldf[(finaldf["jobtitle"].str.contains("Developer")) | (finaldf["jobtitle"].str.contains("Engineer"))]


#Cleaning up and removing duplicates
anotherdf = finaldf[['city', 'company', 'source','date', 'jobkey', 'jobtitle','snippet', 'url']]
anotherdf.set_index('jobkey', inplace=True)
anotherdf['date'] = pd.to_datetime(anotherdf.date)
anotherdf['date'] = anotherdf['date'].apply(lambda x:x.date().strftime('%d/%m/%Y'))
grouped = anotherdf.groupby(level=0)
anotherdf = grouped.last()
anotherdf

#Saving it
letMeChose = filesavebox("Choose a folder","Indeed.xlsx", "indeed",[" *.xlsx"]) 
if letMeChose!=None:
    letMeChose+=".xlsx"
    writer = pd.ExcelWriter(letMeChose, engine='openpyxl')
    anotherdf.to_excel(writer,'Vacancies')
    writer.save()
else:
    print("No folder selected. The program will now close")
    time.sleep(2)
