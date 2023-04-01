import requests
from requests.structures import CaseInsensitiveDict
import pandas as pd
import json
import asana
import datetime
import csv
import config
from urllib.request import urlopen

fosterpath = ''
HWPath = ''
InventoryPath = ''
OutcomePath = ''
CACPath = ''
client = ''

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
    "HOLDNOTIFY" : "1204295300113467",
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

def setClientWithToken(clientjson):
    global client 
    client = clientjson

def setClient():
    global client 
    client = asana.Client.oauth(
    config.client_id,
    config.client_secret,
    redirect_uri='https://127.0.0.1:5000/callback'
    )
    client.headers={"asana-enable": "new_user_task_lists"}
    (url, state) = client.session.authorization_url()
    print("authorized=", client.session.authorized)
    return url

def getProjectMap():
    projects = client.projects.find_by_workspace('1176075726005695')
    projectMap = {}
    for project in projects:
        projectMap[project['name']] = project['gid']
    return projectMap

def getSectionMap(projectName):
    projectMap = getProjectMap()

    sections = client.sections.get_sections_for_project(projectMap[projectName], opt_pretty=True)
    sectionMap = {}
    for section in sections:
        sectionMap[section['name']] = section['gid']
    return sectionMap

def callback(access_token):
    global client 
    token = client.session.fetch_token(code=access_token)
    print("authorized=", client.session.authorized)
    #client = asana.Client.access_token(token)
    
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
        #list.append(d)

def getNewDogs():
    print(client)
    found = True
    last_date = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat() 
    results = []
    resulti = client.tasks.search_tasks_for_workspace('1176075726005695', {'sections.any' : '1201573188659683', 'limit':50, 'completed':False, 'is_subtask':False, 'opt_fields' : ['completed', 'name']}, opt_pretty=True)
    info = []
    for dog in resulti:
        info.append(dog['gid'])
    while found:
        result = client.tasks.search_tasks_for_workspace('1176075726005695', {'projects.any' : '1200600287945473','created_at.before' : last_date, 'sort_by':"created_at", 'limit':50, 'completed':False, 'is_subtask':False, 'opt_fields' : ['custom_fields.name', 'custom_fields.display_value', 'completed', 'name', 'permalink_url', 'created_at']}, opt_pretty=True)
        #result = client.tasks.search_tasks_for_workspace('1176075726005695', {'projects.any' : '1200600287945473', 'limit':50, 'completed':False, 'is_subtask':False, 'opt_fields' : ['custom_fields.name', 'custom_fields.display_value', 'completed', 'name', 'permalink_url']}, opt_pretty=True)
        found = False
        for r in result:
            found = True
            last_date = r["created_at"]
            if r['gid'] in info:
                continue
            else:
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

def getUnsortedRTG():
    print(client)
    found = True
    last_date = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat() 
    results = []
    while found:
        result = client.tasks.search_tasks_for_workspace('1176075726005695', {'projects.any':'1202594804488369', 'created_at.before' : last_date, 'sort_by':"created_at", 'limit':50, 'completed':False, 'is_subtask':False, 'opt_fields' : ['custom_fields.name', 'custom_fields.display_value', 'completed', 'name', 'permalink_url', 'created_at']}, opt_pretty=True)
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

def getUnsortedMT():
    print(client)
    found = True
    last_date = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat() 
    results = []
    while found:
        result = client.tasks.search_tasks_for_workspace('1176075726005695', {'projects.any':'1203676631198131', 'created_at.before' : last_date, 'sort_by':"created_at", 'limit':50, 'completed':False, 'is_subtask':False, 'opt_fields' : ['custom_fields.name', 'custom_fields.display_value', 'completed', 'name', 'permalink_url', 'created_at']}, opt_pretty=True)
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
        try:
            code = dg['Animal ID']        
            if code == None:
                continue
        except:
            continue
        dgs.append(dg)
    return dgs

def getNeedsContentDogs():
    client.headers={"asana-enable": "new_user_task_lists"}
    found = True
    last_date = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat() 
    results = []
    while found:
        result = client.tasks.search_tasks_for_workspace('1176075726005695', {'projects.any':'1200600287945473','projects.not':'1201273747804686','sections.not' : '1201138605268715,1201138605268716','created_at.before' : last_date, 'sort_by':"created_at", 'limit':50, 'completed':False, 'is_subtask':False, 'opt_fields' : ['custom_fields.name', 'custom_fields.display_value', 'completed', 'name', 'permalink_url', 'created_at']}, opt_pretty=True)
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

def getMidtownDogs():
    client.headers={"asana-enable": "new_user_task_lists"}
    found = True
    last_date = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat() 
    results = []
    while found:
        result = client.tasks.search_tasks_for_workspace('1176075726005695', {'projects.any':'1200600287945473','projects.not':'1203676631198131','sections.not' : '1201138605268715,1201138605268716','created_at.before' : last_date, 'sort_by':"created_at", 'limit':50, 'completed':False, 'is_subtask':False, 'opt_fields' : ['custom_fields.name', 'custom_fields.display_value', 'completed', 'name', 'permalink_url', 'created_at']}, opt_pretty=True)
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
        try:
            code = dg['Animal ID']
            if code == None:
                continue
        except:
            continue
        dgs.append(dg)
    return dgs

def getRTGDogs():
    client.headers={"asana-enable": "new_user_task_lists"}
    found = True
    last_date = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat() 
    results = []
    while found:
        result = client.tasks.search_tasks_for_workspace('1176075726005695', {'projects.any':'1200600287945473','projects.not':'1202594804488369','sections.not' : '1201138605268715,1201138605268716','created_at.before' : last_date, 'sort_by':"created_at", 'limit':50, 'completed':False, 'is_subtask':False, 'opt_fields' : ['custom_fields.name', 'custom_fields.display_value', 'completed', 'name', 'permalink_url', 'created_at']}, opt_pretty=True)
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
    
def getFieldMap(projectId):
    #'1200600287945473'
    rslt = client.custom_field_settings.get_custom_field_settings_for_project(projectId,opt_pretty=True)
    fldMap = {}
    picklistMap = {}
    for r in rslt:
        fld = r['custom_field']
        fldMap[fld['name']] = fld['gid']
        if 'enum_options' in fld:
            valueMap = {}
            for val in fld['enum_options']:
                valueMap[val['name']] = val['gid']
            picklistMap[fld['name']] = valueMap
    return fldMap,picklistMap

def getOpenTaskList():
    client.headers={"asana-enable": "new_user_task_lists"}
    found = True
    last_date = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat() 
    results = []
    while found:
        #'projects.any':'1200600287945473',
        #
        result = client.tasks.search_tasks_for_workspace('1176075726005695', {'projects.any':'1200600287945473','created_at.before' : last_date, 'sort_by':"created_at", 'limit':50, 'completed':False, 'is_subtask':False, 'opt_fields' : ['custom_fields.name', 'custom_fields.display_value', 'completed', 'name', 'permalink_url', 'created_at', 'memberships.section.name' , 'memberships.section.project.name']}, opt_pretty=True)
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
        #print(membership)
        for m in membership:
            dg[m['section']['project']['name']+' membership'] = m['section']['name']
        dg['gid'] = task['gid'] 
        for fld in task['custom_fields']:
            dg[fld['name']] = fld['display_value'] 
            #print(dg[fld['name']])
        code = dg['Animal ID']
        if code == None:
            continue
        dgs.append(dg)
    return dgs

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
        aresult = client.tasks.search_tasks_for_workspace('1176075726005695', {'projects.any':'1200600287945473','created_at.before' : last_date, 'sort_by':"created_at", 'limit':50, 'completed':False, 'is_subtask':False, 'opt_fields' : ['custom_fields.name', 'custom_fields.display_value', 'completed', 'name', 'permalink_url', 'created_at','memberships.section.name', 'memberships.section.project.name' ]}, opt_pretty=True)
        found = False
        for r in aresult:
            found = True
            last_date = r["created_at"]
            results.append(r)

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

def moveInCareColumn():
    client.headers={"asana-enable": "new_user_task_lists"}
    dgs = getNewDogs()
    print('got dogs')
    for dog in dgs:    
        kennel = dog['Location']
        if kennel.startswith('A'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1200600287945473','section': '1201521805280278'}, opt_pretty=True)
        elif kennel.startswith('B'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1200600287945473','section': '1200600685971755'}, opt_pretty=True)
        elif kennel.startswith('S'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1200600287945473','section': '1200601235154303'}, opt_pretty=True)
        elif kennel.startswith('J'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1200600287945473','section': '1200601235154304'}, opt_pretty=True)
        elif kennel.startswith('T'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1200600287945473','section': '1200601235154305'}, opt_pretty=True)
        elif kennel.startswith('MID'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1200600287945473','section': '1200601235154306'}, opt_pretty=True)
        elif kennel.startswith('Foster'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1200600287945473','section': '1201138605268716'}, opt_pretty=True)
        else:
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1200600287945473','section': '1200601235154307'}, opt_pretty=True)

def getUnsortedFoster():
    print(client)
    found = True
    last_date = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat() 
    results = []
    while found:
        result = client.tasks.search_tasks_for_workspace('1176075726005695', {'projects.any':'1201449344168303', 'created_at.before' : last_date, 'sort_by':"created_at", 'limit':50, 'completed':False, 'is_subtask':False, 'opt_fields' : ['custom_fields.name', 'custom_fields.display_value', 'completed', 'name', 'permalink_url', 'created_at']}, opt_pretty=True)
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

def moveInFosterColumn():
    client.headers={"asana-enable": "new_user_task_lists"}
    dgs = getUnsortedFoster()
    for dog in dgs:    
        name = dog['name'].lower() 
        #print(name)
        if dog['Location'] != "Foster":
            result = client.tasks.remove_project_for_task(dog['gid'], {'project': '1201449344168303'}, opt_pretty=True)
        elif dog['Reason'] == "EVIDENCE" or dog['Reason'] == "COURT" or dog['Reason'] == "CRUEL INVS":
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1201449344168303','section': '1201449344168314'}, opt_pretty=True)
        elif name.startswith('a') or name.startswith('b') or name.startswith('c') or name.startswith('d'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1201449344168303','section': '1201449344168308'}, opt_pretty=True)
        elif name.startswith('e') or name.startswith('f') or name.startswith('g') or name.startswith('h'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1201449344168303','section': '1201449344168309'}, opt_pretty=True)
        elif name.startswith('i') or name.startswith('j') or name.startswith('k') or name.startswith('l'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1201449344168303','section': '1201449344168310'}, opt_pretty=True)
        elif name.startswith('m') or name.startswith('n') or name.startswith('o') or name.startswith('p'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1201449344168303','section': '1201449344168311'}, opt_pretty=True)
        elif name.startswith('q') or name.startswith('r') or name.startswith('s') or name.startswith('t'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1201449344168303','section': '1201449344168312'}, opt_pretty=True)
        elif name.startswith('u') or name.startswith('v') or name.startswith('w') or name.startswith('x') or name.startswith('y') or name.startswith('z'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1201449344168303','section': '1201449344168313'}, opt_pretty=True)

def moveRTG():
    client.headers={"asana-enable": "new_user_task_lists"}
    dgs = getUnsortedRTG()
    for dog in dgs:    
        kennel = dog['Location'] 
        #print(kennel)
        if kennel.startswith('A'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1202594804488369','section': '1202594804488387'}, opt_pretty=True)
        elif kennel.startswith('B'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1202594804488369','section': '1202594804488388'}, opt_pretty=True)
        elif kennel.startswith('S'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1202594804488369','section': '1202594804488374'}, opt_pretty=True)
        elif kennel.startswith('J'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1202594804488369','section': '1202594804488384'}, opt_pretty=True)
        elif kennel.startswith('T'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1202594804488369','section': '1202594804488383'}, opt_pretty=True)
        elif kennel.startswith('MID'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1202594804488369','section': '1202594804488389'}, opt_pretty=True)
        elif kennel.startswith('CR'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1202594804488369','section': '1202594804488390'}, opt_pretty=True)
        elif kennel.startswith('Foster'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1202594804488369','section': '1202594804488375'}, opt_pretty=True)
        else:
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1202594804488369','section': '1202594804488370'}, opt_pretty=True)

def moveMT():
    client.headers={"asana-enable": "new_user_task_lists"}
    dgs = getUnsortedMT()
    for dog in dgs:    
        kennel = dog['Location']
        if kennel.startswith('MID A'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1203676631198131','section': '1203676631198138'}, opt_pretty=True)
        elif kennel.startswith('MID B'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1203676631198131','section': '1203676631198139'}, opt_pretty=True)
        elif kennel.startswith('MID C'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1203676631198131','section': '1203676631198140'}, opt_pretty=True)
        elif kennel.startswith('MID ISO'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1203676631198131','section': '1203676631198141'}, opt_pretty=True)
        elif kennel.startswith('MID REC'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1203676631198131','section': '1203676631198137'}, opt_pretty=True)
        elif kennel.startswith('MID Q'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1203676631198131','section': '1203676631198142'}, opt_pretty=True)
        elif kennel.startswith('Foster'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1203676631198131','section': '1203676631198148'}, opt_pretty=True)

def getUnsortedWB():
    print(client) 
    results = []
    result = client.tasks.get_tasks_for_project('1202026739375143',{"completed":False,'is_subtask':True,'opt_fields':['custom_fields.name', 'custom_fields.display_value','parent.completed', 'completed']}, opt_pretty=True)
    dgs = []
    for task in result:
        if task['completed'] == False:
            dg = {}
            dg['gid'] = task['gid']
            for fld in task['custom_fields']:
                dg[fld['name']] = fld['display_value']
            if dg['Location'] == None:
                continue
            else:
                dgs.append(dg)
    return dgs

def moveWalkBoard():
    client.headers={"asana-enable": "new_user_task_lists"}
    dgs = getUnsortedWB()
    for dog in dgs:
        kennel = dog['Location']
        if kennel.startswith('S'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1202026739375143','section': '1202026739375144'}, opt_pretty=True)
        elif kennel.startswith('J'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1202026739375143','section': '1202026739375148'}, opt_pretty=True)
        elif kennel.startswith('T'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1202026739375143','section': '1202026739375149'}, opt_pretty=True)
        elif kennel.startswith('A'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1202026739375143','section': '1202036717268960'}, opt_pretty=True)
        elif kennel.startswith('B'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1202026739375143','section': '1202037852728245'}, opt_pretty=True)
        elif kennel.startswith('D'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1202026739375143','section': '1203768970242887'}, opt_pretty=True)
        elif kennel.startswith('MID'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1202026739375143','section': '1203768970242888'}, opt_pretty=True)
        elif kennel.startswith('Foster'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1202026739375143','section': '1203768970242889'}, opt_pretty=True)
        else:
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1202026739375143','section': '1202037852728246'}, opt_pretty=True)

def removeFromContentCreators():
    projectMap = getProjectMap()
    allDogs = getOpenTaskList()
    for dog in allDogs:
        if dog['Hold?'] == None or dog['Hold?'] == 'N':
            continue
        if dog['Reason'] != None:
            if dog['Reason'] == 'MEDICAL' or dog['Reason'] == 'MICROCHIP' or dog['Reason'] == 'CASEWORKER' or dog['Reason'] == 'MOVE UP' or dog['Reason'] == 'DOG TEST' or dog['Reason'] == 'NEED RES':
                continue 
            #print(dog['name'])
            result = client.tasks.remove_project_for_task(dog['gid'], {'project': projectMap['FCAS Content Creators ']}, opt_pretty=True)
            
def addToContentCreators():
    client.headers={"asana-enable": "new_user_task_lists"}
    dgs = getNeedsContentDogs()
    for dog in dgs:    
        if dog['Hold?'] == None or dog['Hold?'] == 'N' or dog['Reason'] == 'CASEWORKER' or dog['Reason'] == 'MICROCHIP' or dog['Reason'] == 'MOVE UP' or dog['Reason'] == 'DOG TEST' or dog['Reason'] == 'NEED RES':
            if dog['Level'] == 'STAFF ONLY':
                continue
            #print(dog)
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1201273747804686'}, opt_pretty=True)

def addToMidtown():
    client.headers={"asana-enable": "new_user_task_lists"}
    dgs = getMidtownDogs()
    for dog in dgs:    
        if dog['Location'].startswith('MID'):
            result = client.tasks.add_project_for_task(dog['gid'], {'project': '1203676631198131'}, opt_pretty=True)

def addToRTG():
    client.headers={"asana-enable": "new_user_task_lists"}
    dgs = getRTGDogs()
    for dog in dgs:    
        if dog['Reason'] == None or dog['Reason'] == 'CASEWORKER' or dog['Reason'] == 'MOVE UP' or dog['Reason'] == 'DOG TEST' or dog['Reason'] == 'NEED RES':
            if dog['Level'] == 'STAFF ONLY':
                result = client.tasks.remove_project_for_task(dog['gid'], {'project': '1202594804488369'}, opt_pretty=True)
                continue
            elif dog['Sex'] != 'N' and dog['Sex'] != 'S':
                result = client.tasks.remove_project_for_task(dog['gid'], {'project': '1202594804488369'}, opt_pretty=True)
                continue
            #print(dog)
            else:
                result = client.tasks.add_project_for_task(dog['gid'], {'project': '1202594804488369'}, opt_pretty=True)
        else:
            result = client.tasks.remove_project_for_task(dog['gid'], {'project': '1202594804488369'}, opt_pretty=True)

def removeRTG():
    projectMap = getProjectMap()
    allDogs = getOpenTaskList()
    for dog in allDogs:
        if dog['Reason'] != None or dog['Level'] == 'STAFF ONLY':
            if dog['Reason'] == 'CASEWORKER' or dog['Reason'] == 'MOVE UP' or dog['Reason'] == 'DOG TEST' or dog['Reason'] == 'NEED RES':
                continue 
            #print(dog['name'])
            result = client.tasks.remove_project_for_task(dog['gid'], {'project': projectMap['FCAS RTG Dogs']}, opt_pretty=True)

def getMiscBehaviorDogs():
    print(client)
    found = True
    last_date = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat() 
    results = []
    while found:
        result = client.tasks.search_tasks_for_workspace('1176075726005695', {'sections.any' : '1202873652030976','created_at.before' : last_date, 'sort_by':"created_at", 'limit':50, 'completed':False, 'is_subtask':False, 'opt_fields' : ['custom_fields.name', 'custom_fields.display_value', 'completed', 'name', 'permalink_url', 'created_at']}, opt_pretty=True)
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

def moveBTdogs():
    try:
        allDogs = getOpenTaskList()
        projectMap = getProjectMap()
        project = projectMap['FCAS Behavior Program']
        sectionMap = getSectionMap('FCAS Behavior Program')
        MiscDogs = getMiscBehaviorDogs()
        miscpups = []
        for pup in MiscDogs:
            miscpups.append(pup['gid'])

        for dog in allDogs:
            if dog['Reason'] == 'BEHAVIOR T':
                #print('BT')
                if dog['Location'] == 'Foster': 
                    result = client.tasks.add_project_for_task(dog['gid'], {'project': project, 'section': sectionMap['In Foster']}, opt_pretty=True)
                else:
                    result = client.tasks.add_project_for_task(dog['gid'], {'project': project, 'section': sectionMap['BT']}, opt_pretty=True)
            elif dog['Reason'] == 'EVALUATE':
                #print('Evaluate')
                if dog['Location'] == 'Foster': 
                    result = client.tasks.add_project_for_task(dog['gid'], {'project': project, 'section': sectionMap['In Foster']}, opt_pretty=True)
                else:
                    result = client.tasks.add_project_for_task(dog['gid'], {'project': project, 'section': sectionMap['Evaluate']}, opt_pretty=True)
            elif dog['Reason'] == 'DECOM':
                #print('Decom')
                if dog['Location'] == 'Foster': 
                    result = client.tasks.add_project_for_task(dog['gid'], {'project': project, 'section': sectionMap['In Foster']}, opt_pretty=True)
                else:
                    result = client.tasks.add_project_for_task(dog['gid'], {'project': project, 'section': sectionMap['DECOM']}, opt_pretty=True)
            elif dog['Level'] == None:
                if dog['gid'] not in miscpups:
                        result = client.tasks.remove_project_for_task(dog['gid'], {'project': project}, opt_pretty=True)
                continue
            elif 'L1' in dog['Level']:
                if dog['gid'] not in miscpups:
                        result = client.tasks.remove_project_for_task(dog['gid'], {'project': project}, opt_pretty=True)
                continue
            elif 'L2' in dog['Level']:
                #print('L2')
                if dog['Location'] == 'Foster': 
                    result = client.tasks.add_project_for_task(dog['gid'], {'project': project, 'section': sectionMap['In Foster']}, opt_pretty=True)
                else:
                    result = client.tasks.add_project_for_task(dog['gid'], {'project': project, 'section': sectionMap['L2']}, opt_pretty=True)
            elif 'L3' in dog['Level']:
                #print('L3')
                if dog['Location'] == 'Foster': 
                    result = client.tasks.add_project_for_task(dog['gid'], {'project': project, 'section': sectionMap['In Foster']}, opt_pretty=True)
                else:
                    result = client.tasks.add_project_for_task(dog['gid'], {'project': project, 'section': sectionMap['L3']}, opt_pretty=True)
            #print('')
        
    except Exception as e:
        print(e)


def updateFromWebsite():
    try:
        dogMap = getWebsiteList()
        allDogs = getOpenTaskList()
        for row in allDogs:
            if row['Animal ID'] in dogMap:
                #print("updating "+row['Animal ID'] )
                dog = dogMap[row['Animal ID']]
                task_gid = row['gid']
                if (dog['name'] != row['name']):
                    t = client.tasks.update_task(task_gid, {'name' : dog['name'],'custom_fields':{'1201541077622257': dog['size_number']}}, opt_pretty=True)
                t = client.tasks.update_task(task_gid, {'custom_fields':{'1201541077622257': dog['size_number']}}, opt_pretty=True)
    except Exception as e:
        print(e)        

def addPicturesToNewDogs():
    try:
        client.headers={"asana-enable": "new_user_task_lists"}
        newdogs = client.tasks.search_tasks_for_workspace('1176075726005695', {'projects.any':'1200600287945473','has_attachment' :False, 'limit':50, 'is_subtask':False, 'opt_fields' : ['custom_fields.name', 'custom_fields.display_value', 'completed', 'name', 'permalink_url', 'created_at']}, opt_pretty=True)
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
            else:
                print(dg['Animal ID'])
            #print (dg)
    except Exception as e: print(e)                                             

def updateFromInventory():
    try:
        print("get tasks")
        dogMap2 = getOpenTasks()
        print("got tasks")
        #i = 0
        with open(InventoryPath, encoding='utf-8-sig') as csvf:
            csvReader = csv.DictReader(csvf)
            for row in csvReader:     
                if row['AID'] not in dogMap2:
                    #print(row['AID'] +" not found") 
                    continue
                task_gid = dogMap2[row['AID']]['gid']
                #print(row['AID'])
                try:
                    custom_fields = {'1200935881386208': row['Kennel'], '1200601343822614' : row['Age'],'1201130160371728': reasondict[row['reason']], '1201130160371724' : holddict[row['hold?']], '1200936046736379': sxdict[row['sx']] }
                    if row['level']:
                        if ("L1" in row['level']):
                            custom_fields['1201130160371745'] = lvldict["L1"]
                            custom_fields['1201718837086260'] = row['level'].replace("L1", "").replace(" ", "")
                        if (row['level'].startswith("L2")):
                            custom_fields['1201130160371745'] = lvldict["L2"]
                            custom_fields['1201718837086260'] = row['level'].replace("L2", "").replace(" ", "")
                        if (row['level'].startswith("L3")):
                            custom_fields['1201130160371745'] = lvldict["L3"]
                            custom_fields['1201718837086260'] = row['level'].replace("L3", "").replace(" ", "")
                        if (row['level'].startswith("Staff Only")):
                            custom_fields['1201130160371745'] = lvldict["STAFF ONLY"]
                            custom_fields['1201718837086260'] = row['level'].replace("STAFF ONLY", "").replace(" ", "")
                        if (row['level'].startswith("STAFF ONLY")):
                            custom_fields['1201130160371745'] = lvldict["STAFF ONLY"]
                            custom_fields['1201718837086260'] = row['level'].replace("STAFF ONLY", "").replace(" ", "")
                    try:
                        t = client.tasks.update_task(task_gid, {'custom_fields':custom_fields}, opt_pretty=True)
                        result = client.tasks.get_subtasks_for_task(task_gid, {'limit':50, 'opt_fields' : ['custom_fields.name', 'custom_fields.display_value', 'completed', 'name', 'permalink_url', 'created_at']}, opt_pretty=True)
                        for r in result:
                            if r['completed'] == True:
                                continue
                            custom_fields['1200601343822598'] = row['AID']
                            st = client.tasks.update_task(r['gid'], {'custom_fields':custom_fields}, opt_pretty=True)
                    except Exception as e:
                        print(e)
                except Exception as e:
                    print(e)
    except Exception as e:
        print(e)        

def updateFosterLocations():
    try:
        dogMap2 = getOpenTasks()
        client.headers={"asana-enable": "new_user_task_lists"}
        with open(fosterpath, encoding='utf-8-sig') as csvf:
            csvReader = csv.DictReader(csvf)
            for row in csvReader:    
                if row['animal_id'] not in dogMap2:
                    continue
                task_gid = dogMap2[row['animal_id']]['gid']
                if row['outcome_subtype'] == 'ADOPTED':
                    result = client.tasks.update_task(task_gid,{'custom_fields':{'1201130160371728': "1201130160371730"}}, opt_pretty=True)
                if row['outcome_subtype'] == 'EVIDENCE':
                    result = client.tasks.update_task(task_gid,{'custom_fields':{'1201130160371728': "1201280909308880"}}, opt_pretty=True)
                if row['outcome_subtype'] == 'TEMP':
                    result = client.tasks.update_task(task_gid,{'custom_fields':{'1201130160371728': "1201197823351018"}}, opt_pretty=True)
                t = client.tasks.update_task(task_gid, {'name': row['animal name'], 'custom_fields':{'1200935881386208': 'Foster', '1200936046736379': sxdict[row['sex']]}}, opt_pretty=True)
                result = client.tasks.get_subtasks_for_task(task_gid, {'limit':50, 'opt_fields' : ['custom_fields.name', 'custom_fields.display_value', 'completed', 'name', 'permalink_url', 'created_at']}, opt_pretty=True)
                for r in result:
                    if r['completed'] == True:
                        continue
                    st = client.tasks.update_task(r['gid'], {'custom_fields':{'1200601343822598' : row['animal_id'],'1200935881386208': 'Foster'}}, opt_pretty=True)
                    if t['custom_fields'][6]['display_value'] != None:
                        st = client.tasks.update_task(r['gid'], {'custom_fields':{'1201130160371728': reasondict[t['custom_fields'][6]['display_value']]}}, opt_pretty=True)
                result = client.tasks.add_project_for_task(task_gid, {'project': '1201449344168303'}, opt_pretty=True)
    except Exception as e:
        print(e) 

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

def getInventory():
    inventory = []
    with open(InventoryPath, encoding='utf-8-sig') as csvf:
        csvReader = csv.DictReader(csvf)
        for row in csvReader:         
            inventory.append(row)
    return inventory

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
            print(row['AID'] + "completed")
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
            if "PERSIAN" in row['description']:
                continue
            if "SPHYNX" in row['description']:
                continue
            if "RUSSIAN BLUE" in row['description']:
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
            if "BIRD" in row['description']:
                continue  
            if "GOAT" in row['description']:
                continue
            if "POSSUM" in row['description']:
                continue   
            if "RAT" in row['description']:
                if "TERRIER" not in row['description']:
                    continue  
            
            #print("not found")
            #print(row)

            if row['name'] == '':
                row['name'] = row['AID']

            try:
                #result = client.tasks.create_task({'projects': ["1200600287945473"], 'workspace': "1176075726005695",'name': row['name'],'custom_fields':{'1200935881386208': row['Kennel'], '1200601343822614' : row['Age'],'1201130160371728': reasondict[row['reason']], '1201130160371724' : holddict[row['hold?']], '1200936046736379': sxdict[row['sx']], '1200601343822598' : row['AID'],'1200936046736386' : row['dob'],'1201248320001333' : row['intake date'],'1200601343822608' : row['description']}}, opt_pretty=True)
                result = client.tasks.duplicate_task('1203768968883595', {'include':["assignee","subtasks","projects","dependencies","dates"],'name': row['name']}, opt_pretty=True)
                custom_fields = {'1200935881386208': row['Kennel'], '1200601343822614' : row['Age'],'1201130160371728': reasondict[row['reason']], '1201130160371724' : holddict[row['hold?']], '1200936046736379': sxdict[row['sx']], '1200601343822598' : row['AID'],'1200936046736386' : row['dob'],'1201248320001333' : row['intake date'],'1200601343822608' : row['description'] }
                if row['level']:
                    if ("L1" in row['level']):
                        custom_fields['1201130160371745'] = lvldict["L1"]
                        custom_fields['1201718837086260'] = row['level'].replace("L1", "").replace(" ", "")
                    if (row['level'].startswith("L2")):
                        custom_fields['1201130160371745'] = lvldict["L2"]
                        custom_fields['1201718837086260'] = row['level'].replace("L2", "").replace(" ", "")
                    if (row['level'].startswith("L3")):
                        custom_fields['1201130160371745'] = lvldict["L3"]
                        custom_fields['1201718837086260'] = row['level'].replace("L3", "").replace(" ", "")
                    if (row['level'].startswith("Staff Only")):
                        custom_fields['1201130160371745'] = lvldict["STAFF ONLY"]
                        custom_fields['1201718837086260'] = row['level'].replace("STAFF ONLY", "").replace(" ", "")
                    if (row['level'].startswith("STAFF ONLY")):
                        custom_fields['1201130160371745'] = lvldict["STAFF ONLY"]
                        custom_fields['1201718837086260'] = row['level'].replace("STAFF ONLY", "").replace(" ", "")
                taskupdate = client.tasks.update_task(result['new_task']['gid'], {'custom_fields':custom_fields}, opt_pretty=True)
                movecol = client.tasks.add_project_for_task(result['new_task']['gid'], {'project': '1200600287945473','section': '1201521805280278'}, opt_pretty=True)
            except Exception as e:
                print(e)

def createMissingFosters():
    try:
        print("authorized=", client.session.authorized)
        notinasana = getFosterNotInAsana()

        completedDogsList = []
        found2 = True
        last_date2 = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat() 
        while found2:
            #'completed':True,
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
        # try:
        #     result = client.tasks.update_task(dg['gid'], {"completed":False}, opt_pretty=True)
        # except Exception as e:
        #     print(e) 
    for row in notinasana:  
        if row['animal_id'] in completedDogs:
            #print("completed")
            row['completed'] = 'False'
        elif row['animal_type'] == 'DOG':           
            #print("not found")
            #print(row)
            if row['animal name'] == '':
                row['animal name'] = row['animal_id']
            try:
                result = client.tasks.duplicate_task('1203768968883595', {'include':["assignee","subtasks","projects","dependencies","dates"],'name': row['animal name']}, opt_pretty=True)
                taskupdate = client.tasks.update_task(result['new_task']['gid'], {'custom_fields':{'1200935881386208': 'Foster', '1200601343822614' : row['years_old'] + ' years ' + row['months_old'] + ' months', '1200936046736379': sxdict[row['sex']], '1200601343822598' : row['animal_id'], '1200601343822608' : row['animal breed']}}, opt_pretty=True)
                movecol = client.tasks.add_project_for_task(result['new_task']['gid'], {'project': '1200600287945473','section': '1201521805280278'}, opt_pretty=True)
                #result = client.tasks.create_task({'projects': ["1200600287945473"], 'workspace': "1176075726005695",'name': row['animal name'],'custom_fields':{'1200935881386208': 'Foster', '1200601343822614' : row['years_old'] + ' years ' + row['months_old'] + ' months', '1200936046736379': sxdict[row['sex']], '1200601343822598' : row['animal_id'], '1200601343822608' : row['animal breed']}}, opt_pretty=True)
            except Exception as e:
                print(e)  

def getFosters():
    fosters = []
    with open(fosterpath, encoding='utf-8-sig') as csvf:
        csvReader = csv.DictReader(csvf)
        for row in csvReader:      
            fosters.append(row)   
            #fosters[row['animal_id']] = row
            #print(row)
    return fosters       

def getFosterNotInAsana():
    dogMap2 = getOpenTasks()
    fosternotinasana = []
    with open(fosterpath, encoding='utf-8-sig') as csvf:
        csvReader = csv.DictReader(csvf)
        for row in csvReader:         
            #print(row)
            if row['animal_id'] not in dogMap2:
                fosternotinasana.append(row)
                continue
            task_gid = dogMap2[row['animal_id']]['gid']
            #t = client.tasks.update_task(task_gid, {'custom_fields':{'1200935881386208': 'Foster'}}, opt_pretty=True)
        #print(fosternotinasana)
        return fosternotinasana

def getHWNotInAsana():
    HWnotinAsana = []
    dogMap2 = getOpenTasks()
    with open(HWPath, encoding='utf-8-sig') as csvf:
        csvReader = csv.DictReader(csvf)
        for row in csvReader:         
            if row['Animal ID'] not in dogMap2:
                HWnotinAsana.append(row)
        return HWnotinAsana

def updateHWStatus():
    client.headers={"asana-enable": "new_user_task_lists"}
    dogMap2 = getOpenTasks()
    with open(HWPath, encoding='utf-8-sig') as csvf:
        csvReader = csv.DictReader(csvf)
        for row in csvReader:        
            if row['Animal ID'] not in dogMap2:
                continue
            task_gid = dogMap2[row['Animal ID']]['gid']
            #print(row['Animal ID'])
            t = client.tasks.update_task(task_gid, {'custom_fields':{'1201160429318661': '1201160429318662'}}, opt_pretty=True)

def searchById(value):
    try:
        r = getFieldMap(getProjectMap()['FCAS Dogs In Care Database'])
        #print(r[0])
        #print()
        #print(r[1]) #Enum map

        #custom_fields.{gid}.contains
        #field matching options
        #contains
        #is_set
        #value (equals)
        #starts_with
        #ends_with
        #less_than
        #greater_than

        fieldMap = r[0]
        idField = fieldMap['Animal ID']
        return client.tasks.search_tasks_for_workspace('1176075726005695', {'custom_fields.'+idField+'.contains': value,'opt_fields' : ['custom_fields.name', 'custom_fields.display_value', 'completed', 'name', 'permalink_url', 'created_at']}, opt_pretty=True)
    except Exception as e:
        print(e)        

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

def cleansubs():
    resulte = client.tasks.search_tasks_for_workspace('1176075726005695', {'sections.any' : '1203768968883583', 'limit':50, 'completed':False, 'is_subtask':False, 'opt_fields' : ['completed', 'name']}, opt_pretty=True)
    resultsp = client.tasks.search_tasks_for_workspace('1176075726005695', {'sections.any' : '1201146133267433', 'limit':50, 'completed':False, 'is_subtask':False, 'opt_fields' : ['completed', 'name']}, opt_pretty=True)
    resultr = client.tasks.search_tasks_for_workspace('1176075726005695', {'sections.any' : '1202891465434971', 'limit':50, 'completed':False, 'is_subtask':False, 'opt_fields' : ['completed', 'name']}, opt_pretty=True)
    info = []
    for dog in resulte:
        info.append(dog['gid'])
    for dog in resultsp:
        info.append(dog['gid'])
    for dog in resultr:
        info.append(dog['gid'])
    result1 = client.tasks.get_tasks_for_project('1203684021953147',{"completed":False,'is_subtask':True,'opt_fields':['parent.completed', 'completed']}, opt_pretty=True)
    for r in result1:
        if r['parent'] == None:
            if r['completed'] == False:
                if r['gid'] in info:
                    continue
                else:
                    print(r)
                    bye = client.tasks.delete_task(r['gid'], opt_pretty=True)
        else:
            if r['parent']['completed'] == True:
                result = client.tasks.get_subtasks_for_task(r['parent']['gid'], {'limit':50, 'opt_fields' : ['custom_fields.name', 'custom_fields.display_value', 'completed', 'name', 'permalink_url', 'created_at', 'projects']}, opt_pretty=True)
                for r in result:
                    if r['completed'] == False:
                        st = client.tasks.update_task(r['gid'], {"completed":True}, opt_pretty=True)

    result2 = client.tasks.get_tasks_for_project('1202026739375143',{"completed":False,'opt_fields':['parent.completed', 'completed']}, opt_pretty=True)
    for r in result2:
        if r['parent'] == None:
            if r['completed'] == False:
                print(r)
                bye = client.tasks.delete_task(r['gid'], opt_pretty=True)
        else:
            if r['parent']['completed'] == True:
                result = client.tasks.get_subtasks_for_task(r['parent']['gid'], {'limit':50, 'opt_fields' : ['custom_fields.name', 'custom_fields.display_value', 'completed', 'name', 'permalink_url', 'created_at', 'projects']}, opt_pretty=True)
                for r in result:
                    if r['projects'] == []:
                        continue
                    elif r['projects'][0]['gid'] == '1202026739375143' and r['completed'] == False:
                        bye = client.tasks.delete_task(r['gid'], opt_pretty=True)

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
        
        #print('done')
        #print(dogMap)

        df = pd.DataFrame(dogMap.values())
        df.to_csv('dogs.csv')
    except Exception as e:
        print(e)        