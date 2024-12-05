from tracemalloc import stop
import wx
from wx import xrc 
import wx.grid as gridlib
#import Audit
import os
import sys
import threading
import queue
import requests
from requests.structures import CaseInsensitiveDict
import pandas as pd
import json
import asana
import datetime
import csv
from urllib.request import urlopen
import asana
import datetime
import pandas as pd
from datetime import date
import time
import pprint
client = asana.Client.access_token('1/1201237139653173:efc34af6c6ee78fe0c4de04b2ea0260a')

def getWebsiteList():
    url = "https://service.api.prd.adopets.app/adopter/pet/find"

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhZG8tYXBpLXNlcnZpY2UiLCJhdWQiOiJwcmQiLCJqdGkiOiIwM2FhOGU0ZS1iYzdlLTRlNGYtYWQ1OS1kNTc5MTZlOWUyN2MiLCJpYXQiOjE3MDUwMDY4NzYuMDg4MTIzLCJsb2dnZWQiOmZhbHNlLCJtb2R1bGUiOiJBRE9QVEVSIn0.Qq3JyOtDVCB7XDqF98go7eYE-6SlHHNuQXvRC9ORQxE"
    headers["Content-Type"] = "application/json"

    data = """
    {"limit":5000,"organization_pet":{"query":""},"branch_uuid":"870a2dd7-5139-497d-b87c-3aa20a59b0fd","origin_key":"IFRAME","user_interaction":true,"shelter_uuid":["e790cdee-169a-491a-abe5-940bfd11afd1"]}
    """
    #CAC shelterId - 42865c72-5efa-4a28-a4b6-edbfaa71ffcf
    resp = requests.post(url, headers=headers, data=data)
    print(resp)
    print(json.loads(resp.text))

    list =[]
    dogMap = {}
    for dog in json.loads(resp.text)['data']['result']:
        d = dog['organization_pet']
        d['age_key'] = d['_formatted']['age_key']
        d['sex_key'] = d['_formatted']['sex_key']
        d['size_key'] = d['_formatted']['size_key']
        d['size_number'] = d['_formatted']['size_number']
        d['mix'] = d['_formatted']['mix']
        d['favorite'] = d['_formatted']['favorite']
        d['application'] = d['_formatted']['application']
        d['price'] = d['_formatted']['price']
        dogMap[d['code']] = d
    return dogMap

website = getWebsiteList().values()
df = pd.DataFrame(website)
df.to_csv('website.csv')
df_fcas = pd.read_csv("FCAS Inventory_FCAS Inventory.csv")
df_fcas['AnimalNumber']=df_fcas['AnimalNumber'].str[3:]
df_website =pd.merge(df_fcas,df,left_on='AnimalNumber',right_on='code',how='outer')
df_website.to_csv('websitemerge.csv')
missing_website = df_website.loc[~df_website['AnimalNumber'].isin(df_website['code'])].reset_index(drop=True)
missing_website = missing_website.loc[(missing_website['Stage'] != 'Bite Quarantine') & (missing_website['Stage'] != 'Court') 
& (missing_website['Stage'] != 'Pre-Euthanasia') & (missing_website['Stage'] != 'Under Age') & (missing_website['Stage'] != 'FTF')
& (missing_website['Stage'] != 'Nursing Mom') & (missing_website['Stage'] != 'TNR') & (missing_website['Stage'] != 'Bite Quarantine - Not Visible')
& (missing_website['Stage'] != 'Pending Behavior Assessment') & (missing_website['Stage'] != 'Pending Medical Assessment/Treatment')
& (missing_website['Stage'] != 'Adopted') & (missing_website['Stage'] != 'Trial Adoption') & (missing_website['SubLocation'] != 'Trial Adoption')
& (missing_website['Stage'] != 'Rescue') & (missing_website['Stage'] != 'Caution-Not Visable')]
missing_website = missing_website.loc[~(missing_website.AnimalName.str.contains('ADOPTED', na=False))]
missing_website.to_csv('websiteissue.csv')