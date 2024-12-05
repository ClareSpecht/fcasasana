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

fosterpath = 'fosterdata (4).csv'
HWPath = 'heartworm positive in shelter 9.10.22.csv'
InventoryPath = 'asana (69).csv'
OutcomePath = 'outcomes 9.9-9.10.csv'

sxdict = {
    "M": "1200936046736380",
    "F": "1200936046736381",
    "N": "1200936046736382",
    "S": "1200936046736383",
    "U": "1200936046736384"
}
reasondict = {
    "ADOPTED PD" : "1201130160371736", 
    "BEHAVIOR T" : "1201130160371738", 
    "CASEWORKER" : "1201130160371729", 
    "CITES" : "1201130160371735", 
    "COURT" : "1201130160371734", 
    "CRUEL INVS" : "1201130160371732", 
    "EVALUATE" : "1201130160371731", 
    "EVIDENCE" : "1201280909308880", 
    "FOS/ADOP" : "1201130160371730", 
    "FOSTER" : "1201130160371743", 
    "MEDICAL" : "1201130160371741",
    "MICROCHIP" : "1201130160371733",
    "MUSTREAD" : "1201130160371737",
    "OWNREQUEST" : "1201130160371742",
    "POSS ADOPT" : "1201130160371739",
    "QUARANTINE" : "1201130160371740",
    "RESCUE" : "1201197823351018",
    "TAG" : "1202542868971212",
    "URGENT": "1202542868971282",
    "CAUTION" : "1202542868970182",
    "DECOM" : "1202542868970177",
    "MOVE UP" : "1202569553756975",
    "PACKET" : "1202569553757013",
    "NEED RES" : "1202691366791659",
    "DOG TEST" : "1202865798846638",
    "UNDERAGE/W" : "1202865777613524",
    "":None
}
holddict = {
    "Y": "1201130160371725",
    "N": "1201130160371726",
    "": "1201130160371726"
}
sxdict = {
    "M": "1200936046736380",
    "F": "1200936046736381",
    "N": "1200936046736382",
    "S": "1200936046736383",
    "U": "1200936046736384"}
lvldict = {
    "L1": "1201130160371746",
    "L2": "1201130160371751",
    "L3" : "1201774420671246",
    "STAFF ONLY": "1201130160371756",
    "":None
}

def getWebsiteList():
    url = "https://adopter.adopets.app/v1/pet/find"

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhcGkucHJvZC5hZG9wZXRzLmNvbSIsImF1ZCI6ImFkb3B0ZXJfc2Vzc2lvbiIsImp0aSI6IjFiNzJjYTYyLTM2ZjItNGU2Ny05ZWI1LTRiZGNlZjc2MjhhYyIsImlhdCI6MTYzMjMyNzM5MCwibG9nZ2VkIjpmYWxzZX0.4rcddCmOpXka8ckob2ZLkylzOyXWCVwUGtWAYATIUsM"
    headers["Content-Type"] = "application/json"

    data = """
    {"limit":500000,"organization_pet":{"query":""},"shelter_uuid":"e790cdee-169a-491a-abe5-940bfd11afd1","origin_key":"IFRAME","user_interaction":true,"branch_uuid":["870a2dd7-5139-497d-b87c-3aa20a59b0fd"]}
    """
    #CAC shelterId - 42865c72-5efa-4a28-a4b6-edbfaa71ffcf
    #branch Id - e790cdee-169a-491a-abe5-940bfd11afd1
    resp = requests.post(url, headers=headers, data=data)

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

def getOpenTasks():
    client.headers={"asana-enable": "new_user_task_lists"}
    dogMap = getWebsiteList()
    results = []
    dogMap2 = {}

    found = True
    # + datetime.timedelta(days=1)
    last_date = (datetime.datetime.now()).isoformat() 
    while found:
        print("getting tasks before "+last_date)
        aresult = client.tasks.search_tasks_for_workspace('1176075726005695', {'projects.any':'1204009005802989','created_at.before' : last_date, 'sort_by':"created_at", 'limit':50, 'completed':False, 'opt_fields' : ['custom_fields.name', 'custom_fields.display_value', 'completed', 'name', 'permalink_url', 'created_at','memberships.section.name', 'memberships.section.project.name' ]}, opt_pretty=True)
        found = False
        for r in aresult:
            found = True
            last_date = r["created_at"]
            results.append(r)
            
    print(results)
    dgs = []
    print('out of while loop')
    for task in results:
        dg = {}
        dg['completed'] = task['completed']
        dg['name'] = task['name']
        dg['permalink_url'] = task['permalink_url']
        dg['gid'] = task['gid']
        for fld in task['custom_fields']:
            dg[fld['name']] = fld['display_value']
        code = dg['Animal ID']
        if code == None:
            continue
        if code in dogMap:
            d = dogMap[code]
            dg['age_key'] = d['age_key']
            dg['sex_key'] = d['sex_key']
            dg['size_key'] = d['size_key']
            dg['size_number'] = d['size_number']
            dg['mix'] = d['mix']
            dg['favorite'] = d['favorite']
            dg['application'] = d['application']
            dg['foster'] = d['foster']
            dg['name'] = d['name']
            dg['breed_primary_name'] = d['breed_primary_name']
            dg['breed_secondary_name'] = d['breed_secondary_name']
            dg['specie_name'] = d['specie_name']
            dg['picture'] = d['picture']
        #else:
            #print(str(code) + " Not Found on website")
            #print(dg)
        dgs.append(dg)
        #print(dg)
        dogMap2[code] = dg
    return dogMap2

def getInventoryDogsNotInAsana():
    try:
        notinasana = []
        dogMap2 = getOpenTasks()
        with open(InventoryPath, encoding='utf-8-sig') as csvf:
            csvReader = csv.DictReader(csvf)
            for row in csvReader:         
                if row['AID'] not in dogMap2:
                    notinasana.append(row)
            return notinasana
    except Exception as e:
        print(e)    

def createMissingDogs():
    try:
        print("authorized=", client.session.authorized)
        notinasana = getInventoryDogsNotInAsana()

        completedDogsList = []
        found2 = True
        last_date2 = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat() 
        while found2:
            alldogs = client.tasks.search_tasks_for_workspace('1176075726005695', {'projects.any':'1200600287945473','created_at.before' : last_date2, 'sort_by':"created_at", 'limit':50, 'is_subtask':False, 'opt_fields' : ['custom_fields.name', 'custom_fields.display_value', 'completed', 'name', 'permalink_url', 'created_at']}, opt_pretty=True)
            found2 = False
            for r in alldogs:
                found2 = True
                last_date2 = r["created_at"]
                dg = {}
                dg['completed'] = r['completed']
                dg['name'] = r['name']
                dg['permalink_url'] = r['permalink_url']
                dg['gid'] = r['gid']
                for fld in r['custom_fields']:
                    dg[fld['name']] = fld['display_value']
                completedDogsList.append(dg)
    except Exception as e:
        print(e)        


    completedDogs = {}
    for dg in completedDogsList:
        code = dg['Animal ID']
        completedDogs[code] = dg #AID
    for row in notinasana:  
        if row['AID'] in completedDogs:
            print("completed")
            # try:
            #     result = client.tasks.update_task(dg['gid'], {"completed":False}, opt_pretty=True)
            # except Exception as e:
            #     print(e)    
        else:
            if "DOMESTIC" in row['description']:
                continue
            if "TABBY" in row['description']:
                continue
            if "SIAMESE" in row['description']:
                continue
            if "SPHYNX" in row['description']:
                continue
            if "PIG" in row['description']:
                continue
            if "SNAKE" in row['description']:
                continue
            if "CHICKEN" in row['description']:
                continue
            if "FERRET" in row['description']:
                continue
            if "RABBIT" in row['description']:
                continue
            if "BAT" in row['description']:
                continue
            if "HAMSTER" in row['description']:
                continue
            if "FREEZER" in row['Kennel']:
                continue
            if "RACCOON" in row['description']:
                continue
            if "TURTLE" in row['description']:
                continue
            if "LIZARD" in row['description']:
                continue     
            if "DUCK" in row['description']:
                continue    
            if "TURKEY" in row['description']:
                continue      
            if "GOAT" in row['description']:
                continue  
            if "RAT" in row['description']:
                continue  

# gids = getOpenTasks()
# print("got tasks")
gids = ['1208174921881568']
for dog in gids:
    print(dog)
    resultw = client.tasks.create_subtask_for_task(dog, {'name': 'Walk or Play Yard Time'}, opt_pretty=True)
    result = client.tasks.add_project_for_task(resultw['gid'], {'project': '1202026739375143'}, opt_pretty=True)
    result9 = client.tasks.create_subtask_for_task(dog, {'name': 'Print Flyer'}, opt_pretty=True)
    result = client.tasks.add_project_for_task(result9['gid'], {'project': '1203684021953147','section': '1203869235142045'}, opt_pretty=True)
    result8 = client.tasks.create_subtask_for_task(dog, {'name': 'Create/Update Flyer'}, opt_pretty=True)
    result = client.tasks.add_project_for_task(result8['gid'], {'project': '1203684021953147','section': '1203684021953160'}, opt_pretty=True)
    result7 = client.tasks.create_subtask_for_task(dog, {'name': 'Print Kennel Flyer'}, opt_pretty=True)
    result = client.tasks.add_project_for_task(result7['gid'], {'project': '1203684021953147','section': '1203869235142044'}, opt_pretty=True)
    result6 = client.tasks.create_subtask_for_task(dog, {'name': 'Create/Update Kennel Flyer'}, opt_pretty=True)
    result = client.tasks.add_project_for_task(result6['gid'], {'project': '1203684021953147','section': '1203684021953159'}, opt_pretty=True)
    result5 = client.tasks.create_subtask_for_task(dog, {'name': 'Update Bio on Website', "assignee": "1204009005802985"}, opt_pretty=True)
    result4 = client.tasks.create_subtask_for_task(dog, {'name': 'Update Bio'}, opt_pretty=True)
    result = client.tasks.add_project_for_task(result4['gid'], {'project': '1203684021953147','section': '1203684021953153'}, opt_pretty=True)
    result3 = client.tasks.create_subtask_for_task(dog, {'name': 'Update Notes'}, opt_pretty=True)
    result = client.tasks.add_project_for_task(result3['gid'], {'project': '1203684021953147','section': '1203684021953152'}, opt_pretty=True)
    result2 = client.tasks.create_subtask_for_task(dog, {'name': 'Update Website Photo', "assignee": "1204009005802985"}, opt_pretty=True)
    result1 = client.tasks.create_subtask_for_task(dog, {'name': 'Update Photo'}, opt_pretty=True)
    result = client.tasks.add_project_for_task(result1['gid'], {'project': '1203684021953147','section': '1203684021953148'}, opt_pretty=True)
    result = client.tasks.add_dependencies_for_task(result2['gid'], {'dependencies': [result1['gid']]}, opt_pretty=True)
    result = client.tasks.add_dependencies_for_task(result4['gid'], {'dependencies': [result3['gid']]}, opt_pretty=True)
    result = client.tasks.add_dependencies_for_task(result5['gid'], {'dependencies': [result4['gid']]}, opt_pretty=True)
    result = client.tasks.add_dependencies_for_task(result6['gid'], {'dependencies': [result1['gid'],result3['gid']]}, opt_pretty=True)
    result = client.tasks.add_dependencies_for_task(result7['gid'], {'dependencies': [result6['gid']]}, opt_pretty=True)
    result = client.tasks.add_dependencies_for_task(result8['gid'], {'dependencies': [result1['gid'],result3['gid']]}, opt_pretty=True)
    result = client.tasks.add_dependencies_for_task(result9['gid'], {'dependencies': [result8['gid']]}, opt_pretty=True)

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

# website = getWebsiteList().values()
# df = pd.DataFrame(website)
# df.to_csv('website.csv')
# df_fcas = pd.read_csv("FCAS Inventory_FCAS Inventory.csv")
# df_fcas['AnimalNumber']=df_fcas['AnimalNumber'].str[3:]
# df_website =pd.merge(df_fcas,df,left_on='AnimalNumber',right_on='code',how='outer')
# missing_website = df_website.loc[~df_website['code'].isin(df_website['AnimalNumber'])].reset_index(drop=True)
# missing_website = missing_website.loc[(missing_website['Stage'] != 'Bite Quarantine') & (missing_website['Stage'] != 'Court') 
# & (missing_website['Stage'] != 'Pre-Euthanasia') & (missing_website['Stage'] != 'Under Age') & (missing_website['Stage'] != 'FTF')
# & (missing_website['Stage'] != 'Nursing Mom') & (missing_website['Stage'] != 'TNR') & (missing_website['Stage'] != 'Bite Quarantine - Not Visible')
# & (missing_website['Stage'] != 'Pending Behavior Assessment') & (missing_website['Stage'] != 'Pending Medical Assessment/Treatment')]
# missing_website.to_csv('websiteissue.csv')