import wx
from wx import xrc 
import wx.grid as gridlib
import Audit
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
import Audit
import asana
from datetime import date
from dateutil.relativedelta import relativedelta
import pandas as pd
import config
client = asana.Client.access_token(config.token)

fosterpath = 'foster report (79).csv'
#HWPath = 'hw+ (61).csv'
InventoryPath = 'asana (111).csv'
#OutcomePath = 'outcomes 9.9-9.10.csv'
today = str(date.today() + relativedelta(weeks=2))
tempupdate = client.tasks.update_task('1204779649606424', {'due_on':today}, opt_pretty=True)

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

def getWebsiteList():
    url = "https://adopter.adopets.app/v1/pet/find"

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhcGkucHJvZC5hZG9wZXRzLmNvbSIsImF1ZCI6ImFkb3B0ZXJfc2Vzc2lvbiIsImp0aSI6IjFiNzJjYTYyLTM2ZjItNGU2Ny05ZWI1LTRiZGNlZjc2MjhhYyIsImlhdCI6MTYzMjMyNzM5MCwibG9nZ2VkIjpmYWxzZX0.4rcddCmOpXka8ckob2ZLkylzOyXWCVwUGtWAYATIUsM"
    headers["Content-Type"] = "application/json"

    data = """
    {"limit":500000,"organization_pet":{"query":""},"shelter_uuid":"e790cdee-169a-491a-abe5-940bfd11afd1","origin_key":"IFRAME","user_interaction":true,"branch_uuid":["870a2dd7-5139-497d-b87c-3aa20a59b0fd"]}
    """
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
        #print(d)
        dogMap[d['code']] = d
    return dogMap
        #list.append(d)

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
        aresult = client.tasks.search_tasks_for_workspace('1176075726005695', {'projects.any':'1201839537137803','created_at.before' : last_date, 'sort_by':"created_at", 'limit':50, 'completed':False, 'is_subtask':False, 'opt_fields' : ['custom_fields.name', 'custom_fields.display_value', 'completed', 'name', 'permalink_url', 'created_at','memberships.section.name', 'memberships.section.project.name' ]}, opt_pretty=True)
        found = False
        for r in aresult:
            found = True
            last_date = r["created_at"]
            results.append(r)

    dgs = []
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
        # else:
            # print(str(code) + " Not Found on website")
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
                    # print('Not in Asana')
                    # print(row)
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
            #'completed':True,
            alldogs = client.tasks.search_tasks_for_workspace('1176075726005695', {'projects.any':'1201839537137803','created_at.before' : last_date2, 'sort_by':"created_at", 'limit':50, 'is_subtask':False, 'opt_fields' : ['custom_fields.name', 'custom_fields.display_value', 'completed', 'name', 'permalink_url', 'created_at']}, opt_pretty=True)
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
            # print("completed")
            row['completed'] = 'False'
        else:
            if "DOMESTIC" in row['description'] or "TABBY" in row['description'] or "SIAMESE" in row['description'] or "RUSSIAN BLUE" in row['description'] or "PERSIAN" in row['description'] or "SPHYNX" in row['description'] or "TURKISH ANGORA" in row['description']:
                if "FREEZER" in row['Kennel']:
                    continue            
                # print("not found")
                # print(row)
                try:
                    result = client.tasks.duplicate_task('1204779649606422', {'include':["assignee","subtasks","projects","dependencies","dates"],'name': row['name']}, opt_pretty=True)
                    taskupdate = client.tasks.update_task(result['new_task']['gid'],{'custom_fields':{'1200935881386208': row['Kennel'], '1200601343822614' : row['Age'],'1201130160371728': reasondict[row['reason']], '1201130160371724' : holddict[row['hold?']], '1200936046736379': sxdict[row['sx']], '1200601343822598' : row['AID'],'1200936046736386' : row['dob'],'1201248320001333' : row['intake date'],'1200601343822608' : row['description']}}, opt_pretty=True)
                    #result = client.tasks.create_task({'projects': ["1201839537137803"], 'workspace': "1176075726005695",'name': row['name'],'custom_fields':{'1200935881386208': row['Kennel'], '1200601343822614' : row['Age'],'1201130160371728': reasondict[row['reason']], '1201130160371724' : holddict[row['hold?']], '1200936046736379': sxdict[row['sx']], '1200601343822598' : row['AID'],'1200936046736386' : row['dob'],'1201248320001333' : row['intake date'],'1200601343822608' : row['description']}}, opt_pretty=True)
                except Exception as e:
                    print(e)

def getFosterNotInAsana():
    dogMap2 = getOpenTasks()
    fosternotinasana = []
    with open(fosterpath, encoding='utf-8-sig') as csvf:
        csvReader = csv.DictReader(csvf)
        for row in csvReader:         
            if row['animal_id'] not in dogMap2:
                fosternotinasana.append(row)
                continue
            task_gid = dogMap2[row['animal_id']]['gid']
        return fosternotinasana

def createMissingFosters():
    try:
        print("authorized=", client.session.authorized)
        notinasana = getFosterNotInAsana()

        completedDogsList = []
        found2 = True
        last_date2 = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat() 
        while found2:
            #'completed':True,
            alldogs = client.tasks.search_tasks_for_workspace('1176075726005695', {'projects.any':'1201839537137803','created_at.before' : last_date2, 'sort_by':"created_at", 'limit':50, 'is_subtask':False, 'opt_fields' : ['custom_fields.name', 'custom_fields.display_value', 'completed', 'name', 'permalink_url', 'created_at']}, opt_pretty=True)
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
        if row['animal_id'] in completedDogs:
            #print("completed")
            row['completed'] = 'False'
        elif row['animal_type'] == 'CAT':           
            # print("not found")
            # print(row)
            try:
                result = client.tasks.duplicate_task('1204779649606422', {'include':["assignee","subtasks","projects","dependencies","dates"],'name': row['animal name']}, opt_pretty=True)
                taskupdate = client.tasks.update_task(result['new_task']['gid'],{'custom_fields':{'1200935881386208': 'Foster', '1200601343822614' : row['years_old'] + ' years ' + row['months_old'] + ' months', '1200936046736379': sxdict[row['sex']], '1200601343822598' : row['animal_id'], '1200601343822608' : row['animal breed']}}, opt_pretty=True)
                # result = client.tasks.create_task({'projects': "1201839537137803", 'workspace': "1176075726005695",'name': row['animal name'],'custom_fields':{'1200935881386208': 'Foster', '1200601343822614' : row['years_old'] + ' years ' + row['months_old'] + ' months', '1200936046736379': sxdict[row['sex']], '1200601343822598' : row['animal_id'], '1200601343822608' : row['animal breed']}}, opt_pretty=True)
            except Exception as e:
                print(e)  

def getOpenTaskList():
    client.headers={"asana-enable": "new_user_task_lists"}
    found = True
    last_date = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat() 
    results = []
    while found:
        result = client.tasks.search_tasks_for_workspace('1176075726005695', {'projects.any':'1201839537137803','created_at.before' : last_date, 'sort_by':"created_at", 'limit':50, 'completed':False, 'is_subtask':False, 'opt_fields' : ['custom_fields.name', 'custom_fields.display_value', 'completed', 'name', 'permalink_url', 'created_at', 'memberships.section.name' , 'memberships.section.project.name']}, opt_pretty=True)
        found = False
        for r in result:
            found = True
            last_date = r["created_at"]
            results.append(r)
    dgs = []
    for task in results:
        dg = {}
        dg['completed'] = task['completed']
        dg['name'] = task['name']
        dg['permalink_url'] = task['permalink_url']
        membership = task['memberships']
        # print(membership)
        for m in membership:
            dg[m['section']['project']['name']+' membership'] = m['section']['name']
        dg['gid'] = task['gid'] 
        for fld in task['custom_fields']:
            dg[fld['name']] = fld['display_value'] 
            # print(dg[fld['name']])
        code = dg['Animal ID']
        if code == None:
            continue
        dgs.append(dg)
    return dgs

print(InventoryPath)
print(fosterpath)
print("create missing cats")
createMissingDogs()
createMissingFosters()

#Update from website
try:
    dogMap = getWebsiteList()
    allDogs = getOpenTaskList()
    for row in allDogs:
        if row['Animal ID'] in dogMap:
            # print("updating "+row['Animal ID'] )
            dog = dogMap[row['Animal ID']]
            task_gid = row['gid']
            # if (dog['name'] != row['name']):
            #     t = client.tasks.update_task(task_gid, {'name' : dog['name'],'custom_fields':{'1201541077622257': dog['size_number']}}, opt_pretty=True)
            t = client.tasks.update_task(task_gid, {'custom_fields':{'1201541077622257': dog['size_number']}}, opt_pretty=True)
except Exception as e:
    print(e)    

#Add Pictures
try:
    client.headers={"asana-enable": "new_user_task_lists"}
    newdogs = client.tasks.search_tasks_for_workspace('1176075726005695', {'projects.any':'1201839537137803','has_attachment' :False, 'limit':50, 'is_subtask':False, 'opt_fields' : ['custom_fields.name', 'custom_fields.display_value', 'completed', 'name', 'permalink_url', 'created_at']}, opt_pretty=True)
    dogMap = getWebsiteList()
    for r in newdogs:
        last_date2 = r["created_at"]
        dg = {}
        dg['completed'] = r['completed']
        dg['name'] = r['name']
        dg['permalink_url'] = r['permalink_url']
        dg['gid'] = r['gid']
        for fld in r['custom_fields']:
            dg[fld['name']] = fld['display_value']
        if dg['Animal ID'] in dogMap:
            d = dogMap[dg['Animal ID']]
            #result = client.attachments.create_attachment_for_task(dg['gid'], {'parent' : dg['gid'],'url': d['picture'],'name':'website.jpg', 'resource_subtype':'external'}, opt_pretty=True)
            img = urlopen(d['picture'].replace('https', 'http')).read()
            client.attachments.create_attachment_for_task(dg['gid'],file_content=img, file_name = 'website.JPEG',file_content_type='image/jpeg') 
        # else:
            # print(dg['Animal ID'])
        #print (dg)
except Exception as e: print(e)

#Update From Inventory
try:
    print("get tasks")
    dogMap2 = getOpenTasks()
    print("got tasks")
    #i = 0
    with open(InventoryPath, encoding='utf-8-sig') as csvf:
        csvReader = csv.DictReader(csvf)
        for row in csvReader:     
            if row['AID'] not in dogMap2:
                # print(row['AID'] +" not found") 
                continue
            task_gid = dogMap2[row['AID']]['gid']
            # print(row['AID'])
            try:
                custom_fields = {'1200935881386208': row['Kennel'], '1201248320001333' : row['intake date'], '1200601343822614' : row['Age'],'1201130160371728': reasondict[row['reason']], '1201130160371724' : holddict[row['hold?']], '1200936046736379': sxdict[row['sx']] }
                try:
                    t = client.tasks.update_task(task_gid, {'name': row['name'], 'custom_fields':custom_fields}, opt_pretty=True)
                except Exception as e:
                    print(e)
            except Exception as e:
                print(e)
except Exception as e:
    print(e)        

#Update From Foster
try:
    dogMap2 = getOpenTasks()
    client.headers={"asana-enable": "new_user_task_lists"}
    with open(fosterpath, encoding='utf-8-sig') as csvf:
        csvReader = csv.DictReader(csvf)
        resulte = client.tasks.search_tasks_for_workspace('1176075726005695', {'sections.any' : '1201845629243908', 'limit':100, 'completed':False, 'is_subtask':False, 'opt_fields' : ['completed', 'name']}, opt_pretty=True)
        resultsp = client.tasks.search_tasks_for_workspace('1176075726005695', {'sections.any' : '1201845449859543', 'limit':100, 'completed':False, 'is_subtask':False, 'opt_fields' : ['completed', 'name']}, opt_pretty=True)
        resultsa = client.tasks.search_tasks_for_workspace('1176075726005695', {'sections.any' : '1204643488018758', 'limit':100, 'completed':False, 'is_subtask':False, 'opt_fields' : ['completed', 'name']}, opt_pretty=True)
        resultsr = client.tasks.search_tasks_for_workspace('1176075726005695', {'sections.any' : '1203151497470569', 'limit':100, 'completed':False, 'is_subtask':False, 'opt_fields' : ['completed', 'name']}, opt_pretty=True)
        info = []
        for dog in resulte:
            info.append(dog['gid'])
        for dog in resultsp:
            info.append(dog['gid'])
        for dog in resultsa:
            info.append(dog['gid'])
        for dog in resultsr:
            info.append(dog['gid'])
        print(info)
        result = client.users.get_users_for_workspace('1176075726005695',{'opt_fields' : ['email']}, opt_pretty=True)
        userlist = []
        for r in result:
            userlist.append(r)
        for row in csvReader:      
            # result = client.tasks.add_project_for_task(task_gid, {'project': '1201839537137838'}, opt_pretty=True)
            if row['animal_id'] not in dogMap2:
                continue
            task_gid = dogMap2[row['animal_id']]['gid']
            email = row['email_addr']
            try:
                result = list(filter(lambda person: person['email'] == email.lower(), userlist))
                assignee = result[0]['gid']
                t = client.tasks.update_task(task_gid, {'name': row['animal name'], "assignee": assignee, 'custom_fields':{'1200935881386208': 'Foster', '1201248320001333' : row['outcome_date'], '1200936046736379': sxdict[row['sex']]}}, opt_pretty=True)
                print(task_gid)
            except:
                print(email)
                t = client.tasks.update_task(task_gid, {'name': row['animal name'], 'custom_fields':{'1200935881386208': 'Foster', '1201248320001333' : row['outcome_date'], '1200936046736379': sxdict[row['sex']]}}, opt_pretty=True)
            if row['outcome_subtype'] == 'ADOPTED':
                result = client.tasks.update_task(task_gid,{'custom_fields':{'1201130160371728': "1201130160371730"}}, opt_pretty=True)
                result = client.tasks.add_project_for_task(task_gid, {'project': '1201839537137838','section': '1202901598685368'}, opt_pretty=True)
            elif row['outcome_subtype'] == 'FOUND':
                result = client.tasks.add_project_for_task(task_gid, {'project': '1201839537137838','section': '1202982227736709'}, opt_pretty=True)
            elif row['outcome_subtype'] == 'TEMP':
                result = client.tasks.update_task(task_gid,{'custom_fields':{'1201130160371728': "1201197823351018"}}, opt_pretty=True)
                result = client.tasks.add_project_for_task(task_gid, {'project': '1201839537137838','section': '1203151497470569'}, opt_pretty=True)
            else:
                if task_gid in info:
                    continue
                else:
                    result = client.tasks.update_task(task_gid,{'custom_fields':{'1201130160371728': None}}, opt_pretty=True)
                    result = client.tasks.add_project_for_task(task_gid, {'project': '1201839537137838','section': '1201845449830973'}, opt_pretty=True)
except Exception as e:
    print(e) 

#Sort Tasks
def getUnsortedRTG():
    print(client)
    found = True
    last_date = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat() 
    results = []
    while found:
        result = client.tasks.search_tasks_for_workspace('1176075726005695', {'projects.any':'1201839537137803', 'created_at.before' : last_date, 'sort_by':"created_at", 'limit':50, 'completed':False, 'is_subtask':False, 'opt_fields' : ['custom_fields.name', 'custom_fields.display_value', 'completed', 'name', 'permalink_url', 'created_at']}, opt_pretty=True)
        found = False
        for r in result:
            found = True
            last_date = r["created_at"]
            results.append(r)
    dgs = []
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
        dgs.append(dg)
    return dgs

client.headers={"asana-enable": "new_user_task_lists"}
dgs = getUnsortedRTG()
resulte = client.tasks.search_tasks_for_workspace('1176075726005695', {'sections.any' : '1204502801611055', 'limit':50, 'completed':False, 'is_subtask':False, 'opt_fields' : ['completed', 'name']}, opt_pretty=True)
resultsp = client.tasks.search_tasks_for_workspace('1176075726005695', {'sections.any' : '1201839537137808', 'limit':50, 'completed':False, 'is_subtask':False, 'opt_fields' : ['completed', 'name']}, opt_pretty=True)
info = []
for dog in resulte:
    info.append(dog['gid'])
for dog in resultsp:
    info.append(dog['gid'])
print(info)
for dog in dgs:    
    kennel = dog['Location']
    hold = dog['Reason']
    if kennel == 'Foster':
        result = client.tasks.add_project_for_task(dog['gid'], {'project': '1201839537137803','section': '1201845629243996'}, opt_pretty=True)
        # result = client.tasks.add_project_for_task(dog['gid'], {'project': '1201839537137838'}, opt_pretty=True)
    elif hold == 'RESCUE' or hold == 'NEED RES':
        result = client.tasks.add_project_for_task(dog['gid'], {'project': '1201839537137803','section': '1204502801611057'}, opt_pretty=True)
    elif hold == 'MICROCHIP':
        result = client.tasks.add_project_for_task(dog['gid'], {'project': '1201839537137803','section': '1202163059344411'}, opt_pretty=True)
    elif hold == 'FOSTER': 
        result = client.tasks.add_project_for_task(dog['gid'], {'project': '1201839537137803','section': '1204502801611055'}, opt_pretty=True)
    elif hold == 'QUARANTINE': 
        result = client.tasks.add_project_for_task(dog['gid'], {'project': '1201839537137803','section': '1204502801611056'}, opt_pretty=True)
    elif kennel != 'Foster':
        if dog['gid'] in info:
            continue
        else:
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1201839537137803','section': '1201839537137804'}, opt_pretty=True)
    if kennel != 'Foster':
        result = client.tasks.remove_project_for_task(dog['gid'], {'project': '1201839537137838'}, opt_pretty=True)
        
#Audit report
def getOpenTaskList():
    client.headers={"asana-enable": "new_user_task_lists"}
    found = True
    last_date = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat() 
    results = []
    while found:
        result = client.tasks.search_tasks_for_workspace('1176075726005695', {'projects.any':'1201839537137803','created_at.before' : last_date, 'sort_by':"created_at", 'limit':50, 'completed':False, 'is_subtask':False, 'opt_fields' : ['custom_fields.name', 'custom_fields.display_value', 'completed', 'name', 'permalink_url', 'created_at', 'memberships.section.name' , 'memberships.section.project.name']}, opt_pretty=True)
        found = False
        for r in result:
            found = True
            last_date = r["created_at"]
            results.append(r)
    dgs = []
    for task in results:
        dg = {}
        dg['completed'] = task['completed']
        dg['name'] = task['name']
        dg['permalink_url'] = task['permalink_url']
        membership = task['memberships']
        # print(membership)
        for m in membership:
            dg[m['section']['project']['name']+' membership'] = m['section']['name']
        dg['gid'] = task['gid'] 
        for fld in task['custom_fields']:
            dg[fld['name']] = fld['display_value'] 
            # print(dg[fld['name']])
        code = dg['Animal ID']
        if code == None:
            continue
        dgs.append(dg)
    return dgs

def getInventory():
    inventory = []
    with open(InventoryPath, encoding='utf-8-sig') as csvf:
        csvReader = csv.DictReader(csvf)
        for row in csvReader:         
            inventory.append(row)
    return inventory

def getFosters():
    fosters = []
    with open(fosterpath, encoding='utf-8-sig') as csvf:
        csvReader = csv.DictReader(csvf)
        for row in csvReader:      
            fosters.append(row)   
            #fosters[row['animal_id']] = row
            # print(row)
    return fosters

def addAudit(dogMap, lst, keystr, typ):
    for dog in lst:
        d = {}
        code = dog[keystr] 
        if code in dogMap:
            d = dogMap[dog[keystr]]
        for key in dog.keys():
            d[typ +' '+ key] = dog[key]
            d[typ] = True
        dogMap[dog[keystr]] = d
    return dogMap

def runAudit():
    try:
        dogMap = {}
        tasks = getOpenTaskList()#getOpenTasks().values()
        
        if InventoryPath != None and InventoryPath != '':
            inventory = getInventory()
            dogMap = addAudit(dogMap, inventory, 'AID', 'inventory')
        if fosterpath != None and fosterpath != '':
            fosters = getFosters()
            dogMap = addAudit(dogMap, fosters, 'animal_id', 'foster')
        website = getWebsiteList().values()

        dogMap = addAudit(dogMap, tasks, 'Animal ID', 'task')
        dogMap = addAudit(dogMap, website, 'code', 'website')

        df = pd.DataFrame(dogMap.values())
        df.to_csv('cats.csv')
    except Exception as e:
        print(e)        

runAudit()