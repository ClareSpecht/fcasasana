from cgitb import small
from cmath import nan
from copyreg import remove_extension
from itertools import count
import re
from sqlite3 import Row
from tracemalloc import stop
from unittest import result, skip
from urllib import request
import os
import sys
import threading
import queue
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import concurrent.futures
import asana
import datetime
import pprint
import numpy as np
import math
import traceback
from urllib.request import urlopen
# import gspread
import requests
import xml.etree.ElementTree as ET
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
from email import encoders, header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from numpy import NAN, NaN
import base64
import pickle
from datetime import datetime
from datetime import date
from google.oauth2.credentials import Credentials
import json
import sys
from bs4 import BeautifulSoup
import config

import fcas_config
dictionary= fcas_config.dictionary()
df_membership={}
SCOPES = ['https://mail.google.com/']
hw =  {'Positive': '1201160429318662',"High Positive":"1201160429318662", 'Negative': '1201160429318663', 'Low Positive':'1201160429318662'}

client = asana.Client.access_token(config.token)

def check_enum():
    setClientWithToken(client)
    result = client.custom_field_settings.get_custom_field_settings_for_project('1200600287945473', opt_pretty=True) 

    dicti = {}
    pp = pprint.PrettyPrinter(indent=3)
    for x in result:
        dicti_temp ={}
        temp={}
        temp['gid']=x['custom_field']['gid']
        try:
            for y in x['custom_field']['enum_options']:
                dicti_temp[y['name']]=y['gid']
                temp['options']=dicti_temp
        except:
            print("not enum")
        dicti[x['custom_field']['name']]=temp
    dictionary['fields']=dicti
     
    file1 = open("dict.txt","w")
    file1.write(pp.pformat(dictionary))
    file1.close()
    return 

def create_new_enum(df):
    print(df.size)
    print(df.columns)
    dicti = dictionary['enum']
    df=df[dicti['df_fields_keep']]
    list_of_fields =dicti['df_switch']
    list_of_dfs={}
    for x in dicti['df_fields_keep']:
        x_df = df[x].drop_duplicates()
        print(x_df)
        x_df = x_df.tolist()
        list_of_dfs[x]=x_df
    new_enum_dict =[]
    print(list_of_dfs)
    for fields,list_of_unique_vals in list_of_dfs.items():
        value = dicti['df_switch'][fields]
        # new_enum_needed=[]
        for x in list_of_unique_vals:
            try:
                dictionary['fields'][value]['options'][x]
            except:
                new_enum_dict.append([dictionary['fields'][value]['gid'],x])
        # new_enum_dict.append(new_enum_needed)
    counter = 0
    counter_two = 0
    print("number enum add: "+str(len(new_enum_dict)))
    if(len(new_enum_dict)>0):
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        # client.tasks.update_task(row[39],{'custom_fields':options},opt_pretty=True)
            future_to_url = {executor.submit(new_enum,key[0],key[1]): key for key in new_enum_dict}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    counter+=1
                    print(future.result())
                except BaseException as err:
                    counter_two+=1
                    print("error")
                    print(err.args)
        print("number added: "+str(counter))
        print("errors: "+str(counter_two))
    
    return counter

def new_enum(gid,value):
    result = client.custom_fields.create_enum_option_for_custom_field(gid, {'color': 'blue', 'name': str(value)}, opt_pretty=True)
    return result

def setClientWithToken(clientjson):
    global client 
    client = clientjson
    return

def pandatime():
    df_fcas = pd.read_csv("FCAS Inventory_FCAS Inventory.csv")

    # drop_cols = ['Location_1', 'AVG_LOS', 'Distinct_Animals', 
    # 'Declawed',
    #    'PreAltered', 'IntakeType',
    #    'ChipNumber', 'Species', 
    #    'EmancipationDate',
    #    'StageChangeReason',
    #    'Danger', 'DangerType', 'NumberOfPictures', 'Videos', 'HoldReason',
    #    'HorForName', 'HoldStartDate', 'HoldPlacedBy', 'Total_Animals']
    # dict_name = {
    #     'AnimalNumber':"AID",
    # }
   
    # df_fcas = df_fcas.drop(columns=drop_cols)

    # df_behavior = pd.read_csv("BehaviorTestHistory.csv",skiprows=3,encoding='utf-8')
    df_behavior = pd.read_csv("FCAS Behavior_FCAS Behavior.csv",skiprows=2,encoding='utf-8')
    df_behavior = df_behavior[['BehaviorTest', 'Animal #', 'Notes','TestCategory','Date']]
    df_behavior[['Date', 'Time']] = df_behavior['Date'].str.split(' ', n=1, expand=True)
    df_behavior.to_csv('Behavior1.csv')
    df_behavior['Notes'] = df_behavior['Date'] + ' ' + df_behavior['Notes']
    df_behavior = df_behavior.reset_index(drop=True)
    #df_behavior = df_behavior.loc[(df_behavior['TestCategory'] == 'In Shelter Volunteer Observation') | (df_behavior['TestCategory'] == 'Staff Observation')].reset_index(drop=True)
    #CLEANR = re.compile('<.*?>|&.+;')
    i = 0
    for row in df_behavior['Notes']:
        string = str(row)
        new_string = string.replace("Notes: ", "" )
        #cleantext = re.sub(CLEANR, '', new_string)
        cleantext = BeautifulSoup(new_string, "html.parser").text
        cleantext = cleantext.replace('\U0001f49b', "")
        df_behavior['Notes'][i] = cleantext
        i = i + 1
    
    df_behavior.to_csv("Behavior2.csv")

    dog_test = df_behavior.loc[df_behavior['BehaviorTest'] == 'Interaction - Dog to Dog']
    dog_test = dog_test.groupby(['Animal #'])['Notes'].apply('\n\n'.join).reset_index()
    dog_test = dog_test.rename(columns={"Notes":"DogTest"})
    dog_test.to_csv("DogTest.csv")

    playgroup = df_behavior.loc[df_behavior['BehaviorTest'] == 'Playgroup']
    playgroup = playgroup.groupby(['Animal #'])['Notes'].apply('\n\n'.join).reset_index()
    playgroup = playgroup.rename(columns={"Notes":"PlayGroup"})
    playgroup.to_csv("PlayGroup.csv")

    behavior = df_behavior.loc[(df_behavior['TestCategory'] == 'In Shelter Volunteer Observation') | (df_behavior['TestCategory'] == 'Staff Observation') | (df_behavior['TestCategory'] == 'Trainer Notes')].reset_index(drop=True)
    behavior = behavior.loc[~(behavior['BehaviorTest'] == 'Interaction - Dog to Dog')].reset_index(drop=True)
    behavior = behavior.groupby(['Animal #'])['Notes'].apply('\n\n'.join).reset_index()
    behavior = behavior.rename(columns={"Notes":"Behavior"})
    behavior.to_csv("Behavior.csv")

    homenotes = df_behavior.loc[(df_behavior['TestCategory'] == 'DFTD/Field Trip') | (df_behavior['TestCategory'] == 'Home Notes') | (df_behavior['TestCategory'] == 'Other')].reset_index(drop=True)
    homenotes = homenotes.groupby(['Animal #'])['Notes'].apply('\n\n'.join).reset_index()
    homenotes = homenotes.rename(columns={"Notes":"HomeNotes"})
    homenotes.to_csv("HomeNotes.csv")

    #df_fcas_hw = pd.read_csv("MedicalTestsDetail.csv",skiprows=6)
    df_fcas_hw = pd.read_csv("FCAS HW_FCAS HW.csv",skiprows=2)

    #df_fcas_hw = pd.read_csv("MedicalTestsDetail.csv",skiprows=6)
    df_fcas_rabies = pd.read_csv("FCAS Rabies_FCAS Rabies.csv",skiprows=2)

    #df_fcas_foster = pd.read_csv("FosterCurrent.csv",skiprows=6)
    df_fcas_foster = pd.read_csv("FCAS Foster_FCAS Foster.csv",skiprows=2)

    #df_fcas_hold = pd.read_csv("HoldingCurrent.csv",skiprows=3)
    df_fcas_hold = pd.read_csv("FCAS Holds_FCAS Holds.csv",skiprows=2)

    df_fcas_url = pd.read_csv("FCAS Short URL_FCAS Short URL.csv",skiprows=2)

    #df_fcas_hw = df_fcas_hw[['Textbox2','Result']]
    df_fcas_hw = df_fcas_hw[['Animal #','Result']]
    df_fcas =pd.merge(df_fcas,df_fcas_hw, how='left',right_on='Animal #',left_on='AnimalNumber')
    df_fcas =pd.merge(df_fcas,df_fcas_rabies, how='left',right_on='Animal #',left_on='AnimalNumber')
    #df_fcas_foster = df_fcas_foster[['textbox9','FosterReason']]
    df_fcas_foster = df_fcas_foster[['Animal #','FosterReason']]
    df_fcas =pd.merge(df_fcas,df_fcas_foster, how='left',right_on='Animal #',left_on='AnimalNumber')
    df_fcas_url = df_fcas_url[['Animal #','ShortURL']]
    df_fcas =pd.merge(df_fcas,df_fcas_url, how='left',right_on='Animal #',left_on='AnimalNumber')
    # df_fcas_hold = df_fcas_hold[['textbox67','textbox15']]
    df_fcas_hold = df_fcas_hold[['Animal #','HoldReason']]
    #df_fcas_hold = df_fcas_hold.rename(columns={"textbox15":"HoldReason"})
    #df_fcas_hold["HoldReason"] = df_fcas_hold["HoldReason"].str[1:]
    df_fcas =pd.merge(df_fcas,df_fcas_hold, how='left',right_on='Animal #',left_on='AnimalNumber')
    df_fcas =pd.merge(df_fcas,dog_test, how='left',right_on='Animal #',left_on='AnimalNumber')
    df_fcas =pd.merge(df_fcas,playgroup, how='left',right_on='Animal #',left_on='AnimalNumber')
    df_fcas =pd.merge(df_fcas,behavior, how='left',right_on='Animal #',left_on='AnimalNumber')
    df_fcas =pd.merge(df_fcas,homenotes, how='left',right_on='Animal #',left_on='AnimalNumber')
    df_fcas['Location'] = df_fcas['Location'] + ' ' + df_fcas['SubLocation']
    # df_fcas['Color'] = df_fcas[['Color', 'ColorPattern', 'PrimaryBreed', 'SecondaryBreed']].agg(' '.join, axis=1)
    #df_fcas[['AnimalWeight', 'Pounds']] = df_fcas['AnimalWeight'].str.split('.', n=1, expand=True)
    df_fcas[['IntakeDate', 'Time']] = df_fcas['IntakeDateTime'].str.split(' ', n=1, expand=True)
    df_fcas[['DateOfBirth', 'Time2']] = df_fcas['DateOfBirth'].str.split(' ', n=1, expand=True)
    df_fcas[['ExpirationDate', 'Time3']] = df_fcas['ExpirationDate'].str.split(' ', n=1, expand=True)
    df_fcas.to_csv("DF_FCAS_nonreduced.csv")
    df_fcas = df_fcas.drop(columns=['SubLocation','Time','Time2','Time3','Animal #_x','Animal #_y', 'Animal #_x','Animal #_y', 'Animal #_x','Animal #_y', 'Animal #_x','Animal #_y'])
    print(df_fcas['AnimalWeight'].dtypes)
    df_fcas['AnimalWeight'] = np.floor(pd.to_numeric(df_fcas['AnimalWeight'], errors='coerce')).astype('Int64')
    #df_fcas['AnimalWeight'] = df_fcas['AnimalWeight'].astype('Int64')
    df_fcas['AnimalWeight'] = df_fcas['AnimalWeight'].fillna(0)
    df_fcas = df_fcas.loc[df_fcas['AnimalType']=='Dog']
    df_fcas = df_fcas.loc[~(df_fcas.Location.str.contains('Fridge', na=False))]
    df_fcas['Level'] = ''
    df_fcas.loc[df_fcas.ARN.str.contains('L1', na=False), 'Level'] = "L1"
    df_fcas.loc[df_fcas.ARN.str.contains('L2', na=False), 'Level'] = "L2"
    df_fcas.loc[df_fcas.ARN.str.contains('L3', na=False), 'Level'] = "L3"
    df_fcas.loc[df_fcas.ARN.str.contains('Staff', na=False), 'Level'] = "STAFF ONLY"
    df_fcas.loc[df_fcas.ARN.str.contains('STAFF', na=False), 'Level'] = "STAFF ONLY"
    df_fcas.loc[df_fcas.ARN.str.contains('staff', na=False), 'Level'] = "STAFF ONLY"
    #df_fcas.loc[(df_fcas.Sex == 'M') & (df_fcas.SpayedNeutered == 'Y'), 'Sex'] = "N"
    #df_fcas.loc[(df_fcas.Sex == 'F') & (df_fcas.SpayedNeutered == 'Y'), 'Sex'] = "S"
    #df_fcas = df_fcas.replace({np.nan:None})
    print('PetPoint Level Type:')
    print(df_fcas['Level'].dtypes)
    print('PetPoint HW Type:')
    print(df_fcas['Result'].dtypes)
    print('PetPoint Hold Type:')
    print(df_fcas['HoldReason'].dtypes)
    
    df_fcas.to_csv("DF_FCAS_nonreduced.csv")

    return [df_fcas]

def comb_dfs(df_asana,df_fcas,gid_dict):
    outcomes = pd.read_csv("AnimalOutcome.csv",skiprows=3)
    asanaoutcomes = pd.merge(outcomes,df_asana,how="inner",left_on="AnimalNumber",right_on="Animal ID")
    negoutcomes = asanaoutcomes.loc[(asanaoutcomes.textbox16 == 'Died') | (asanaoutcomes.textbox16 == 'Euthanasia')]
    negoutcomes.to_csv("EuthList.csv")

    posoutcomes = asanaoutcomes.loc[(asanaoutcomes['textbox16'] != 'Died') & (asanaoutcomes['textbox16'] != 'Euthanasia')]
    posoutcomes.to_csv("AdoptList.csv")

    matching_fcas_inv = pd.merge(df_fcas,df_asana,how="inner",left_on="AnimalNumber",right_on="Animal ID")
    matching_fcas_inv.to_csv("Matching_fcas_inv.csv")
    df_adopt = matching_fcas_inv.loc[matching_fcas_inv['AnimalName'].str.contains("adopt",case=False,regex=True,na=False)]
    df_adopt=df_adopt.loc[df_adopt['completed']==False]
    print(matching_fcas_inv.shape)
    matching_fcas_inv_correct= matching_fcas_inv.loc[matching_fcas_inv['completed']==False]
    print(matching_fcas_inv_correct.shape)
    matching_fcas_inv_incorrect = matching_fcas_inv.loc[matching_fcas_inv['completed']==True]
    matching_fcas_inv.to_csv("Matching_fcas_inv.csv")
    matching_fcas_inv_incorrect.to_csv("Matching_fcas_inv_incorrect.csv")

    missing_fcas_inv = df_fcas.loc[~df_fcas['AnimalNumber'].isin(df_asana['Animal ID'])].reset_index(drop=True)
    missing_fcas_inv.to_csv("missing_fcas_inv.csv")
    asana_missing_fcas = df_asana.loc[~df_asana['Animal ID'].isin(df_fcas['AnimalNumber'])].reset_index(drop=True)
    asana_missing_fcas.to_csv("asana_missing_fcas.csv")
    asana_missing_fcas = asana_missing_fcas.loc[asana_missing_fcas['completed']==False]
    df_adopt=df_adopt[['gid','AnimalNumber']]
    asana_missing_fcas=asana_missing_fcas.rename(columns={"Animal ID":"AnimalNumber"})
    asana_missing_fcas=asana_missing_fcas[['gid','AnimalNumber']]

    # pathways = matching_fcas_inv_correct.loc[matching_fcas_inv_correct['LOSInDays']>50]
    # pathways = pathways.loc[~(pathways['Stage'] == 'Court')]
    # pathways = pathways.loc[~(pathways.Location_x.str.contains('Foster', na=False))]
    # pathways.to_csv("Pathways.csv")

    rtf = matching_fcas_inv_correct.loc[matching_fcas_inv_correct['Stage'] == 'Available']
    rtf = rtf.loc[(rtf['ExpirationDate'].notna())]
    rtf = rtf.loc[(rtf['MicrochipNumber'].notna())]
    rtf.to_csv("RTF.csv")
    rtg = rtf.loc[(rtf['Sex_x'] == 'S')|(rtf['Sex_x'] == 'N')]
    rtg.to_csv("RTG.csv")
    
    return [matching_fcas_inv,missing_fcas_inv,asana_missing_fcas,matching_fcas_inv_incorrect,negoutcomes,posoutcomes,pathways,rtg,rtf]

def comb_pics(df_asana,df_fcas,gid_dict):
    matching_fcas_inv = pd.merge(df_fcas,df_asana,how="inner",left_on="AnimalNumber",right_on="Animal ID")
    #matching_fcas_inv.to_csv("Matching_pics_inv.csv")
    print(matching_fcas_inv.shape)
    matching_fcas_inv_correct= matching_fcas_inv.loc[matching_fcas_inv['completed']==False]
    print(matching_fcas_inv_correct.shape)
    matching_fcas_inv_incorrect = matching_fcas_inv.loc[matching_fcas_inv['completed']==True]
    
    missing_fcas_inv = df_fcas.loc[~df_fcas['AnimalNumber'].isin(df_asana['Animal ID'])].reset_index(drop=True)
    #missing_fcas_inv.to_csv("missing_web_inv.csv")
    asana_missing_fcas = df_asana.loc[~df_asana['Animal ID'].isin(df_fcas['AnimalNumber'])].reset_index(drop=True)
    #asana_missing_fcas.to_csv("web_missing_fcas.csv")
    asana_missing_fcas = asana_missing_fcas.loc[asana_missing_fcas['completed']==False]
    asana_missing_fcas=asana_missing_fcas.rename(columns={"Animal ID":"AnimalNumber"})
    asana_missing_fcas=asana_missing_fcas[['gid','AnimalNumber']]
    
    return [matching_fcas_inv_correct,missing_fcas_inv,asana_missing_fcas,matching_fcas_inv_incorrect]

def foster_df ():
    setClientWithToken(client)
    (url, state) = client.session.authorization_url()
    print("authorized=", client.session.authorized)
    tasks = client.tasks.get_tasks_for_project(dictionary['projects']['foster']['gid'],{'is_subtask':False,'opt_fields' : ['custom_fields.name', 'custom_fields.display_value','completed', 'name', 'permalink_url', 'created_at','memberships.section.name', 'memberships.section.project.name' ]})
    projectmap={}
    pp = pprint.PrettyPrinter(indent=2)
    column_titles = ['gid']
    gid_dict ={}
    row_df =[]
    counter =True
    
    for r in tasks:
        row_list=[r['gid']]
        len_cols = dictionary['variables']['lenwname']
        for x in r['custom_fields']:
            if(counter):
                gid_dict[x['name']]=x['gid']
                column_titles.append(x['name'])
            row_list.append(x['display_value'])
        row_list.append(r['completed'])
        row_list.append(r['name'])
        temp_member_list = {}
        df_membership[r['gid']]=r['memberships']
        #print(row_list)
        #print(len(row_list))
        if(counter):
            column_titles.append("completed")
            column_titles.append("name")
        if len(row_list)==dictionary['variables']['lenwname']:
            row_df.append(row_list)
            counter=False
        else:
            # print(row_list)
            if(counter ==True):
                column_titles=['gid']   
    print(len(column_titles))
    counter=0
    for x in row_df:
        if(len(x)>dictionary['variables']['lenwname']):           
            print(counter)
            print(row_df[counter])
            row_df.pop(counter)
        counter+=1
    df_foster_database = pd.DataFrame(row_df,columns=column_titles)
    df_foster_database.to_csv("Foster_dataframe.csv")

    return [df_foster_database,gid_dict,df_membership]

def pathways_df ():
    setClientWithToken(client)
    (url, state) = client.session.authorization_url()
    print("authorized=", client.session.authorized)
    tasks = client.tasks.get_tasks_for_project(dictionary['projects']['pathways']['gid'],{'is_subtask':False, "completed_since": "now",'opt_fields' : ['custom_fields.name', 'custom_fields.display_value','completed', 'name', 'permalink_url', 'created_at','memberships.section.name', 'memberships.section.project.name' ]})
    projectmap={}
    pp = pprint.PrettyPrinter(indent=2)
    column_titles = ['gid']
    gid_dict ={}
    row_df =[]
    counter =True
    
    for r in tasks:
        row_list=[r['gid']]
        len_cols = dictionary['variables']['lenwname']
        for x in r['custom_fields']:
            if(counter):
                gid_dict[x['name']]=x['gid']
                column_titles.append(x['name'])
            row_list.append(x['display_value'])
        row_list.append(r['completed'])
        row_list.append(r['name'])
        temp_member_list = {}
        df_membership[r['gid']]=r['memberships']
        #print(row_list)
        #print(len(row_list))
        if(counter):
            column_titles.append("completed")
            column_titles.append("name")
        if len(row_list)==dictionary['variables']['lenwname']:
            row_df.append(row_list)
            counter=False
        else:
            # print(row_list)
            if(counter ==True):
                column_titles=['gid']   
    print(len(column_titles))
    counter=0
    for x in row_df:
        if(len(x)>dictionary['variables']['lenwname']):           
            print(counter)
            print(row_df[counter])
            row_df.pop(counter)
        counter+=1
    df_pathways_database = pd.DataFrame(row_df,columns=column_titles)
    df_pathways_database.to_csv("Pathways_dataframe.csv")

    return [df_pathways_database,gid_dict,df_membership]

def rtg_df ():
    setClientWithToken(client)
    (url, state) = client.session.authorization_url()
    print("authorized=", client.session.authorized)
    tasks = client.tasks.get_tasks_for_project(dictionary['projects']['rtg']['gid'],{'is_subtask':False, "completed_since": "now",'opt_fields' : ['custom_fields.name', 'custom_fields.display_value','completed', 'name', 'permalink_url', 'created_at','memberships.section.name', 'memberships.section.project.name' ]})
    projectmap={}
    pp = pprint.PrettyPrinter(indent=2)
    column_titles = ['gid']
    gid_dict ={}
    row_df =[]
    counter =True
    
    for r in tasks:
        row_list=[r['gid']]
        len_cols = dictionary['variables']['lenwname']
        for x in r['custom_fields']:
            if(counter):
                gid_dict[x['name']]=x['gid']
                column_titles.append(x['name'])
            row_list.append(x['display_value'])
        row_list.append(r['completed'])
        row_list.append(r['name'])
        temp_member_list = {}
        df_membership[r['gid']]=r['memberships']
        #print(row_list)
        #print(len(row_list))
        if(counter):
            column_titles.append("completed")
            column_titles.append("name")
        if len(row_list)==dictionary['variables']['lenwname']:
            row_df.append(row_list)
            counter=False
        else:
            # print(row_list)
            if(counter ==True):
                column_titles=['gid']   
    print(len(column_titles))
    counter=0
    for x in row_df:
        if(len(x)>dictionary['variables']['lenwname']):           
            print(counter)
            print(row_df[counter])
            row_df.pop(counter)
        counter+=1
    df_rtg_database = pd.DataFrame(row_df,columns=column_titles)

    return [df_rtg_database,gid_dict,df_membership]

def rtf_df ():
    setClientWithToken(client)
    (url, state) = client.session.authorization_url()
    print("authorized=", client.session.authorized)
    tasks = client.tasks.get_tasks_for_project(dictionary['projects']['rtf']['gid'],{'is_subtask':False, "completed_since": "now",'opt_fields' : ['custom_fields.name', 'custom_fields.display_value','completed', 'name', 'permalink_url', 'created_at','memberships.section.name', 'memberships.section.project.name' ]})
    projectmap={}
    pp = pprint.PrettyPrinter(indent=2)
    column_titles = ['gid']
    gid_dict ={}
    row_df =[]
    counter =True
    
    for r in tasks:
        row_list=[r['gid']]
        len_cols = dictionary['variables']['lenwname']
        for x in r['custom_fields']:
            if(counter):
                gid_dict[x['name']]=x['gid']
                column_titles.append(x['name'])
            row_list.append(x['display_value'])
        row_list.append(r['completed'])
        row_list.append(r['name'])
        temp_member_list = {}
        df_membership[r['gid']]=r['memberships']
        #print(row_list)
        #print(len(row_list))
        if(counter):
            column_titles.append("completed")
            column_titles.append("name")
        if len(row_list)==dictionary['variables']['lenwname']:
            row_df.append(row_list)
            counter=False
        else:
            # print(row_list)
            if(counter ==True):
                column_titles=['gid']   
    print(len(column_titles))
    counter=0
    for x in row_df:
        if(len(x)>dictionary['variables']['lenwname']):           
            print(counter)
            print(row_df[counter])
            row_df.pop(counter)
        counter+=1
    df_rtf_database = pd.DataFrame(row_df,columns=column_titles)

    return [df_rtf_database,gid_dict,df_membership]

def walk_df ():
    setClientWithToken(client)
    (url, state) = client.session.authorization_url()
    print("authorized=", client.session.authorized)
    tasks = client.tasks.get_tasks_for_project(dictionary['projects']['walk']['gid'],{"completed_since": "now", 'opt_fields' : ['custom_fields.name', 'custom_fields.display_value','completed', 'name', 'permalink_url', 'created_at','memberships.section.name', 'memberships.section.project.name','parent.completed']})
    projectmap={}
    pp = pprint.PrettyPrinter(indent=2)
    column_titles = ['gid']
    gid_dict ={}
    row_df =[]
    counter =True
    
    for r in tasks:
        row_list=[r['gid']]
        len_cols = dictionary['variables']['len_walk']
        for x in r['custom_fields']:
            if(counter):
                gid_dict[x['name']]=x['gid']
                column_titles.append(x['name'])
            row_list.append(x['display_value'])
        row_list.append(r['completed'])
        if r['parent'] == None:
            row_list.append(None)
            row_list.append(None)
        else:
            row_list.append(r['parent']['gid'])
            row_list.append(r['parent']['completed'])
        temp_member_list = {}
        df_membership[r['gid']]=r['memberships']

        if(counter):
            column_titles.append("completed")
            column_titles.append("parent gid")
            column_titles.append("parent completed")
        if len(row_list)==dictionary['variables']['len_walk']:
            row_df.append(row_list)
            counter=False
        else:
            # print(row_list)
            if(counter ==True):
                column_titles=['gid']   
    print(len(column_titles))

    counter=0
    for x in row_df:
        if(len(x)>dictionary['variables']['len_walk']):           
            print(counter)
            print(row_df[counter])
            row_df.pop(counter)
        counter+=1
    df_walk_database = pd.DataFrame(row_df,columns=column_titles)
    df_walk_database.to_csv("WalkBoard.csv")

    return [df_walk_database,gid_dict,df_membership]


def content_df ():
    setClientWithToken(client)
    (url, state) = client.session.authorization_url()
    print("authorized=", client.session.authorized)
    tasks = client.tasks.get_tasks_for_project(dictionary['projects']['content']['gid'],{"completed_since": "now", 'opt_fields' : ['custom_fields.name', 'custom_fields.display_value','completed', 'name', 'permalink_url', 'created_at','memberships.section.name', 'memberships.section.project.name','parent.completed']})
    projectmap={}
    pp = pprint.PrettyPrinter(indent=2)
    column_titles = ['gid']
    gid_dict ={}
    row_df =[]
    counter =True
    
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

    for r in tasks:
        if r['gid'] in info:
            continue
        row_list=[r['gid']]
        len_cols = dictionary['variables']['len_walk']
        for x in r['custom_fields']:
            if(counter):
                gid_dict[x['name']]=x['gid']
                column_titles.append(x['name'])
            row_list.append(x['display_value'])
        row_list.append(r['completed'])
        if r['parent'] == None:
            row_list.append(None)
            row_list.append(None)
        else:
            row_list.append(r['parent']['gid'])
            row_list.append(r['parent']['completed'])
        temp_member_list = {}
        df_membership[r['gid']]=r['memberships']

        if(counter):
            column_titles.append("completed")
            column_titles.append("parent gid")
            column_titles.append("parent completed")
        if len(row_list)==dictionary['variables']['len_walk']:
            row_df.append(row_list)
            counter=False
        else:
            # print(row_list)
            if(counter ==True):
                column_titles=['gid']   
    print(len(column_titles))

    counter=0
    for x in row_df:
        if(len(x)>dictionary['variables']['len_walk']):           
            print(counter)
            print(row_df[counter])
            row_df.pop(counter)
        counter+=1
    df_content_database = pd.DataFrame(row_df,columns=column_titles)
    df_content_database.to_csv("ContentBoard.csv")

    return [df_content_database,gid_dict,df_membership]

def remove_old(dfneg,dfpos):
    list_to_complete = dfpos['gid']
    print(list_to_complete)
    counter = 0
    counter_two = 0
    print("number to complete: "+str(len(list_to_complete)))
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        future_to_url = {executor.submit(outcome,row): row for row in list_to_complete}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                counter+=1
                # print(future.result())
            except BaseException as err:
                counter_two+=1
                print("error")
                print(err.args)
    print("number completed: "+str(counter))   
    print("errors: "+str(counter_two))

    list_to_delete = dfneg['gid']
    print(list_to_delete)
    for gid in list_to_delete:
        print(gid)
        result = client.tasks.delete_task(gid, opt_pretty=True)

    return

def outcome(gid):
    #print(gid)
    result = client.tasks.update_task(gid, {"completed":True}, opt_pretty=True)
    return result

def update_existing(df):
    pp = pprint.PrettyPrinter(indent=2)
    
    df=df[dictionary['update_existing']['df_fields_keep']]
    df.to_csv("updatething.csv")
    diction ={}
    init_list = dictionary['update_existing']['update_fields']
    counter =0
    for row in df.itertuples(index=False):
        temp={}
        for x in init_list:
            try:
                dict_val = dictionary['update_existing']['df_switch'][x]
            except:
                dict_val=x
            temp_dict = dictionary["fields"][dict_val]
            try:
                if(math.isnan(getattr(row,x))):
                    print(x +" is nan")
                    temp[temp_dict['gid']] = None
                    continue
            except:
                pass
            if(x=='Result'):
                if(isinstance(getattr(row,x),str)):
                    try:
                        temp[temp_dict['gid']]=hw[getattr(row,x)]
                    except:
                        continue
            else:
                try:
                    value = temp_dict['options'][getattr(row,x)]
                    temp[temp_dict['gid']]=str(temp_dict['options'][getattr(row,x)])
                except:
                    temp[temp_dict['gid']]=str(getattr(row,x))
        diction[str(getattr(row,'gid'))]={'name':getattr(row,'AnimalName'),'custom_fields':temp}
    file1 = open("tempupdate.txt","w",encoding="utf-8")
    file1.write(pp.pformat(diction))
    file1.close()
    counter = 0
    failed = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(update, gid,options): gid for gid,options in diction.items()}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                counter+=1
                # print(future.result())
            except Exception as exc:
                print(exc)
                failed+=1
    print("update_number: "+str(counter))
    print("failed number: "+str(failed))
    return

def update(gid,options):
    result = client.tasks.update_task(gid,options,opt_pretty=True)
    if (options['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Featured')) or (options['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Flex')):
        section ={'project':dictionary['projects']['main']['gid'],'section':dictionary['projects']['main']['sections']['Featured']}
    elif (options['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Dogs 0')):
        section ={'project':dictionary['projects']['main']['gid'],'section':dictionary['projects']['main']['sections']['0']}
    elif (options['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Dogs 3')):
        section ={'project':dictionary['projects']['main']['gid'],'section':dictionary['projects']['main']['sections']['3']}
    elif (options['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Dogs 4')):
        section ={'project':dictionary['projects']['main']['gid'],'section':dictionary['projects']['main']['sections']['4']}
    elif (options['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Dogs 5')):
        section ={'project':dictionary['projects']['main']['gid'],'section':dictionary['projects']['main']['sections']['5']}
    elif (options['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Dogs 6')):
        section ={'project':dictionary['projects']['main']['gid'],'section':dictionary['projects']['main']['sections']['6']}
    elif (options['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Caseworker')) or (options['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Dogs 2')):
        section ={'project':dictionary['projects']['main']['gid'],'section':dictionary['projects']['main']['sections']['CW']}
    elif (options['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Dog ISO')) or (options['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Dog Q')):
        section ={'project':dictionary['projects']['main']['gid'],'section':dictionary['projects']['main']['sections']['ISO']}
    elif 'Foster' in (options['custom_fields'][dictionary['fields']['Location']['gid']]):
        section ={'project':dictionary['projects']['main']['gid'],'section':dictionary['projects']['main']['sections']['Foster']}
        fos_result = client.tasks.add_project_for_task(gid, {'project': dictionary['projects']['foster']['gid']}, opt_pretty=True)
    else:
        section ={'project':dictionary['projects']['main']['gid'],'section':dictionary['projects']['main']['sections']['Other']}
    meh_result = client.tasks.add_project_for_task(gid, section, opt_pretty=True)

    return result

def update_walks(df):
    pp = pprint.PrettyPrinter(indent=2)
    
    df=df[dictionary['update_walks']['df_fields_keep']]
    df.to_csv("updatewalks.csv")
    diction ={}
    init_list = dictionary['update_walks']['update_fields']
    #print(init_list)
    counter =0
    for row in df.itertuples(index=False):
        temp={}
        for x in init_list:
            try:
                dict_val = dictionary['update_walks']['df_switch'][x]
            except:
                dict_val=x
            #print(dict_val)
            temp_dict = dictionary["fields"][dict_val]
            try:
                if(math.isnan(getattr(row,x))):
                    print(x +" is nan")
                    continue
            except:
                pass
            try:
                value = temp_dict['options'][getattr(row,x)]
                #print(value)
                temp[temp_dict['gid']]=str(temp_dict['options'][getattr(row,x)])
            except:
                temp[temp_dict['gid']]=str(getattr(row,x))
        diction[str(getattr(row,'gid_x'))]={'custom_fields':temp}
    file1 = open("tempupdate.txt","w")
    file1.write(pp.pformat(diction))
    file1.close()
    counter = 0
    failed = 0

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_url = {executor.submit(updatewalk, gid,options): gid for gid,options in diction.items()}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                counter+=1
                # print(future.result())
            except Exception as exc:
                print(exc)
                failed+=1
    print("update_number: "+str(counter))
    print("failed number: "+str(failed))
    return

def updatewalk(gid,options):
    #Won't update if level or HW is blank!
    result = client.tasks.update_task(gid,options,opt_pretty=True)
    if (options['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Featured')) or (options['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Flex')):
        section ={'project':dictionary['projects']['walk']['gid'],'section':dictionary['projects']['walk']['sections']['Featured']}
    elif (options['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Dogs 0')):
        section ={'project':dictionary['projects']['walk']['gid'],'section':dictionary['projects']['walk']['sections']['0']}
    elif (options['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Dogs 6')):
        section ={'project':dictionary['projects']['walk']['gid'],'section':dictionary['projects']['walk']['sections']['6']}
    elif (options['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Dogs 5')):
        section ={'project':dictionary['projects']['walk']['gid'],'section':dictionary['projects']['walk']['sections']['5']}
    elif (options['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Dogs 4')):
        section ={'project':dictionary['projects']['walk']['gid'],'section':dictionary['projects']['walk']['sections']['4']}
    elif 'Foster' in (options['custom_fields'][dictionary['fields']['Location']['gid']]):
        section ={'project':dictionary['projects']['walk']['gid'],'section':dictionary['projects']['walk']['sections']['Foster']}
    elif (options['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Dogs 3')):
        section ={'project':dictionary['projects']['walk']['gid'],'section':dictionary['projects']['walk']['sections']['3']}
    elif (options['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Caseworker')) or (options['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Dogs 2')):
        section ={'project':dictionary['projects']['walk']['gid'],'section':dictionary['projects']['walk']['sections']['CW']}
    elif (options['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Dog ISO')):
        section ={'project':dictionary['projects']['walk']['gid'],'section':dictionary['projects']['walk']['sections']['ISO']}
    elif (options['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Dog Q')):
        section ={'project':dictionary['projects']['walk']['gid'],'section':dictionary['projects']['walk']['sections']['Q']}
    else:
        section ={'project':dictionary['projects']['walk']['gid'],'section':dictionary['projects']['walk']['sections']['Other']}
    meh_result = client.tasks.add_project_for_task(gid, section, opt_pretty=True)

    if 'Foster' in (options['custom_fields'][dictionary['fields']['Location']['gid']]):
        client.tasks.update_task(gid, {"completed":True}, opt_pretty=True)

    return result

def update_content(df):
    pp = pprint.PrettyPrinter(indent=2)
    
    df=df[dictionary['update_walks']['df_fields_keep']]
    df.to_csv("updatecontent.csv")
    diction ={}
    init_list = dictionary['update_walks']['update_fields']
    #print(init_list)
    counter =0
    for row in df.itertuples(index=False):
        temp={}
        for x in init_list:
            try:
                dict_val = dictionary['update_walks']['df_switch'][x]
            except:
                dict_val=x
            #print(dict_val)
            temp_dict = dictionary["fields"][dict_val]
            try:
                if(math.isnan(getattr(row,x))):
                    print(x +" is nan")
                    continue
            except:
                pass
            try:
                value = temp_dict['options'][getattr(row,x)]
                #print(value)
                temp[temp_dict['gid']]=str(temp_dict['options'][getattr(row,x)])
            except:
                temp[temp_dict['gid']]=str(getattr(row,x))
        diction[str(getattr(row,'gid_x'))]={'custom_fields':temp}
    file1 = open("tempupdate.txt","w")
    file1.write(pp.pformat(diction))
    file1.close()
    counter = 0
    failed = 0

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_url = {executor.submit(updatecontent, gid,options): gid for gid,options in diction.items()}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                counter+=1
                # print(future.result())
            except Exception as exc:
                print(exc)
                failed+=1
    print("update_number: "+str(counter))
    print("failed number: "+str(failed))
    return

def updatecontent(gid,options):
    #Won't update if level is blank!
    result = client.tasks.update_task(gid,options,opt_pretty=True)

    return result

def pathways (df1,df2):
    pp = pprint.PrettyPrinter(indent=2)
    df1=df1.loc[df1['completed']==False]

    for row in df2.index:
        if df2['Animal ID'][row] is None:
            continue
        elif 'Foster' in df2['Location'][row]:
            #print(df2['Animal ID'][row])
            result = client.tasks.remove_project_for_task(df2['gid'][row], {'project': dictionary['projects']['pathways']['gid']}, opt_pretty=True)

    for row in df1.index:
        result = client.tasks.add_project_for_task(df1['gid'][row], {'project': dictionary['projects']['pathways']['gid']}, opt_pretty=True)

    return

def rtg (df1,df2):
    pp = pprint.PrettyPrinter(indent=2)

    rtglist = []
    for dog in df1.index:
        rtglist.append(df1['AnimalNumber'][dog])
    
    #print(rtglist)

    for row in df2.index:
        if df2['Animal ID'][row] not in rtglist:
            result = client.tasks.remove_project_for_task(df2['gid'][row], {'project': dictionary['projects']['rtg']['gid']}, opt_pretty=True)

    for row in df1.index:        
        if pd.isna(df1['Location_x'][row]):
            continue
        elif (df1['Location_x'][row].startswith('Featured')) or (df1['Location_x'][row].startswith('Flex')):
            section ={'project':dictionary['projects']['rtg']['gid'],'section':dictionary['projects']['rtg']['sections']['Featured']}
        elif (df1['Location_x'][row].startswith('Dogs 0')):
            section ={'project':dictionary['projects']['rtg']['gid'],'section':dictionary['projects']['rtg']['sections']['0']}
        elif (df1['Location_x'][row].startswith('Dogs 3')):
            section ={'project':dictionary['projects']['rtg']['gid'],'section':dictionary['projects']['rtg']['sections']['3']}
        elif (df1['Location_x'][row].startswith('Dogs 4')):
            section ={'project':dictionary['projects']['rtg']['gid'],'section':dictionary['projects']['rtg']['sections']['4']}
        elif (df1['Location_x'][row].startswith('Dogs 5')):
            section ={'project':dictionary['projects']['rtg']['gid'],'section':dictionary['projects']['rtg']['sections']['5']}
        elif (df1['Location_x'][row].startswith('Dogs 6')):
            section ={'project':dictionary['projects']['rtg']['gid'],'section':dictionary['projects']['rtg']['sections']['6']}
        elif 'Foster' in (df1['Location_x'][row]):
            section ={'project':dictionary['projects']['rtg']['gid'],'section':dictionary['projects']['rtg']['sections']['Foster']}
        else:
            section ={'project':dictionary['projects']['rtg']['gid'],'section':dictionary['projects']['rtg']['sections']['Other']}
        result = client.tasks.add_project_for_task(df1['gid'][row], section, opt_pretty=True)

    return

def rtf (df1,df2):
    pp = pprint.PrettyPrinter(indent=2)

    rtglist = []
    for dog in df1.index:
        rtglist.append(df1['AnimalNumber'][dog])
    
    #print(rtglist)

    for row in df2.index:
        if df2['Animal ID'][row] not in rtglist:
            result = client.tasks.remove_project_for_task(df2['gid'][row], {'project': dictionary['projects']['rtf']['gid']}, opt_pretty=True)

    for row in df1.index:        
        if pd.isna(df1['Location_x'][row]):
            continue
        elif (df1['Location_x'][row].startswith('Featured')) or (df1['Location_x'][row].startswith('Flex')):
            section ={'project':dictionary['projects']['rtf']['gid'],'section':dictionary['projects']['rtf']['sections']['Featured']}
        elif (df1['Location_x'][row].startswith('Dogs 0')):
            section ={'project':dictionary['projects']['rtf']['gid'],'section':dictionary['projects']['rtf']['sections']['0']}
        elif (df1['Location_x'][row].startswith('Dogs 3')):
            section ={'project':dictionary['projects']['rtf']['gid'],'section':dictionary['projects']['rtf']['sections']['3']}
        elif (df1['Location_x'][row].startswith('Dogs 4')):
            section ={'project':dictionary['projects']['rtf']['gid'],'section':dictionary['projects']['rtf']['sections']['4']}
        elif (df1['Location_x'][row].startswith('Dogs 5')):
            section ={'project':dictionary['projects']['rtf']['gid'],'section':dictionary['projects']['rtf']['sections']['5']}
        elif (df1['Location_x'][row].startswith('Dogs 6')):
            section ={'project':dictionary['projects']['rtf']['gid'],'section':dictionary['projects']['rtf']['sections']['6']}
        elif 'Foster' in (df1['Location_x'][row]):
            section ={'project':dictionary['projects']['rtf']['gid'],'section':dictionary['projects']['rtf']['sections']['Foster']}
        else:
            section ={'project':dictionary['projects']['rtf']['gid'],'section':dictionary['projects']['rtf']['sections']['Other']}
        result = client.tasks.add_project_for_task(df1['gid'][row], section, opt_pretty=True)

    return

def foster (df):
    pp = pprint.PrettyPrinter(indent=2)
    df=df.loc[df['completed']==False]

    for row in df.index:
        #print(df['name'][row])
        if 'Foster' not in (df['Location'][row]):
            result = client.tasks.remove_project_for_task(df['gid'][row], {'project': dictionary['projects']['foster']['gid']}, opt_pretty=True)
            continue
        elif (df['Current Status'][row]) == 'Court':
            section ={'project':dictionary['projects']['foster']['gid'],'section':dictionary['projects']['foster']['sections']['LEF']}
        else:
            section ={'project':dictionary['projects']['foster']['gid'],'section':dictionary['projects']['foster']['sections'][df['name'][row][0].upper()]}
        meh_result = client.tasks.add_project_for_task(df['gid'][row], section, opt_pretty=True)        
    
    return

def create_new(df):
    today = str(date.today())
    tempupdate = client.tasks.update_task('1206398747883088', {'due_on':today}, opt_pretty=True)
    
    pp = pprint.PrettyPrinter(indent=2)
    df=df[dictionary['create_new']['df_fields_keep']]
    
    df.loc[:, 'projects']=dictionary["projects"]['main']['gid']
    counter =0

    init_list = list(df.columns)
    for x in dictionary['create_new']['new_remove']:
        init_list.remove(x)

    new_pets =[]
    for row in df.itertuples(index=False):
        data = {    
            "data": {
                "name":row.AnimalName,
                "projects":[row.projects],
                "resource_subtype": "default_task"
            }
            }
        temp={}
        for x in init_list:
            # print(dictionary['fields'])
            try:
                dict_val = dictionary['create_new']['df_switch'][x]
            except:
                dict_val=x
            temp_dict = dictionary['fields'][dict_val]
            if(x=='Result'):
                if(isinstance(getattr(row,x),str)):
                    try:
                        temp[temp_dict['gid']]=hw[getattr(row,x)]
                    except:
                        continue
            elif(x=='AnimalWeight'):
                # print("weight 1")
                # print(getattr(row,x))
                # print(type(getattr(row,x)))
                if(isinstance(getattr(row,x),str)):
                    # print("weight")
                    temp[temp_dict['gid']]=getattr(row,x)
            else:
                try:
                    if math.isnan(getattr(row,x)):
                        #print(x)
                        continue
                    else:
                        try:
                            temp[temp_dict['gid']]=str(temp_dict['options'][getattr(row,x)])
                        except:
                            temp[temp_dict['gid']]=str(getattr(row,x))
                except:
                    try:
                        temp[temp_dict['gid']]=str(temp_dict['options'][getattr(row,x)])
                    except:
                        temp[temp_dict['gid']]=str(getattr(row,x))
        # temp[dictionary['fields']['has_attachment']['gid']]=dictionary['fields']['has_attachment']['options']['False']
        data['data']['custom_fields']=temp
        new_pets.append(data)
    # pp.pprint(new_pets)
    file1 = open("tempnewupdate.txt","w")
    file1.write(pp.pformat(new_pets))
    file1.close()
        # json_object = json.loads(data)
        # data['data']['Name']='TEST'
    new_gid ={}
    counter = 0
    #troubleshooting

    # for data in new_pets:
    #     pp.pprint(data)
    #     if (data['data']['custom_fields']['1202731630315875']=='1202731630315877') or (data['data']['custom_fields']['1202731630315875']=='1202731630315876'):
    #         print("lvl1 or lvl2")
    #     create_new_pets(data)
    #     counter+=1
    #     if counter ==4:
    #         break
    # return
    with concurrent.futures.ThreadPoolExecutor() as executor:
    # client.tasks.update_task(row[39],{'custom_fields':options},opt_pretty=True)
        future_to_url = {executor.submit(create_new_pets,data): data for data in new_pets}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                # new_gid['']
                
                counter+=1
                
                print(future.result())
            except BaseException as err:
                print(err.args)
                
        # except:
            # print(row[3])
    return counter

def bring_back_old(df):
    list_to_add= df[dictionary['bring_back_old']['df_fields_keep']].unique().tolist()
    counter = 0
    counter_two = 0
    print("number to add: "+str(len(list_to_add)))
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
    # client.tasks.update_task(row[39],{'custom_fields':options},opt_pretty=True)
        future_to_url = {executor.submit(intake_old,row): row for row in list_to_add}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                counter+=1
                print(url)
                # print(future.result())
            except BaseException as err:
                counter_two+=1
                print("error")
                print(err.args)
    print("number removed: "+str(counter))
    print("errors: "+str(counter_two))
    return

def intake_old(gid):
    #print(gid)
    result = client.tasks.update_task(gid, {"completed":False}, opt_pretty=True)
    subresult = client.tasks.duplicate_task('1206398747883088', {'include':["assignee","subtasks","projects","dependencies","dates","parent"], 'name':'Walk or Play Yard Time'}, opt_pretty=True)
    #print(subresult['new_task']['gid'])
    api_response = client.tasks.set_parent_for_task(subresult['new_task']['gid'], {'parent':gid, 'insert_before': None}, opt_pretty=True)
    return result

def create_new_pets(data):
    if data['data']['name'] is nan:
        data['data']['name'] = data['data']['custom_fields'][dictionary['fields']['Animal ID']['gid']]
    result = client.tasks.duplicate_task('1206386867201919', {'include':["assignee","subtasks","projects","dependencies","dates"],'name': data['data']['name']}, opt_pretty=True)
    taskupdate = client.tasks.update_task(result['new_task']['gid'], {'custom_fields':data['data']['custom_fields']}, opt_pretty=True)
    #print(taskupdate)
    # result = client.tasks.create_task(data['data'], opt_pretty=True)
    if (data['data']['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Featured')) or (data['data']['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Flex')):
        #print(data['data']['custom_fields'][dictionary['fields']['Location']['gid']])
        section ={'project':dictionary['projects']['main']['gid'],'section':dictionary['projects']['main']['sections']['Featured']}
    elif (data['data']['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Dogs 0')):
        #print(data['data']['custom_fields'][dictionary['fields']['Location']['gid']])
        section ={'project':dictionary['projects']['main']['gid'],'section':dictionary['projects']['main']['sections']['0']}
    elif (data['data']['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Dogs 3')):
        #print(data['data']['custom_fields'][dictionary['fields']['Location']['gid']])
        section ={'project':dictionary['projects']['main']['gid'],'section':dictionary['projects']['main']['sections']['3']}
    elif (data['data']['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Dogs 4')):
        #print(data['data']['custom_fields'][dictionary['fields']['Location']['gid']])
        section ={'project':dictionary['projects']['main']['gid'],'section':dictionary['projects']['main']['sections']['4']}
    elif (data['data']['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Dogs 5')):
        #print(data['data']['custom_fields'][dictionary['fields']['Location']['gid']])
        section ={'project':dictionary['projects']['main']['gid'],'section':dictionary['projects']['main']['sections']['5']}
    elif (data['data']['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Dogs 6')):
        #print(data['data']['custom_fields'][dictionary['fields']['Location']['gid']])
        section ={'project':dictionary['projects']['main']['gid'],'section':dictionary['projects']['main']['sections']['6']}
    elif (data['data']['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Caseworker')) or (data['data']['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Dogs 2')):
        #print(data['data']['custom_fields'][dictionary['fields']['Location']['gid']])
        section ={'project':dictionary['projects']['main']['gid'],'section':dictionary['projects']['main']['sections']['CW']}
    elif (data['data']['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Dog ISO')) or (data['data']['custom_fields'][dictionary['fields']['Location']['gid']].startswith('Dog Q')):
        #print(data['data']['custom_fields'][dictionary['fields']['Location']['gid']])
        section ={'project':dictionary['projects']['main']['gid'],'section':dictionary['projects']['main']['sections']['ISO']}
    elif 'Foster' in (data['data']['custom_fields'][dictionary['fields']['Location']['gid']]):
        #print(data['data']['custom_fields'][dictionary['fields']['Location']['gid']])
        section ={'project':dictionary['projects']['main']['gid'],'section':dictionary['projects']['main']['sections']['Foster']}
    else:
        #print(data['data']['custom_fields'][dictionary['fields']['Location']['gid']])
        section ={'project':dictionary['projects']['main']['gid'],'section':dictionary['projects']['main']['sections']['Other']}
    
    client.tasks.add_project_for_task(result['new_task']['gid'], section, opt_pretty=True)

    #print(data['data']['custom_fields'])

    return result

def walkclean(walktasks,maintasks):
    negoutcomes = walktasks.loc[(walktasks['parent completed'].isnull())]
    negoutcomes.to_csv("DeleteWalks.csv")
    posoutcomes = walktasks.loc[(walktasks['parent completed'] == True)]
    posoutcomes.to_csv("CompleteWalks.csv")

    remove_old(negoutcomes, posoutcomes)

    active = walktasks.loc[(walktasks['parent completed'] == False)]
    children = pd.merge(active,maintasks,how="inner",left_on="parent gid",right_on="gid")
    children['AnimalID'] = children['Animal ID_y']
    children['CurrentStatus'] = children['Current Status_y']
    children['LevelReason'] = children['Level Reason_y']
    print('FCAS Asana Walk Column type:')
    print(children['Level_y'].dtypes)
    children.to_csv("WalkParents.csv")

    return children

def contentclean(contenttasks,maintasks):
    negoutcomes = contenttasks.loc[(contenttasks['parent completed'].isnull())]
    negoutcomes.to_csv("DeleteContent.csv")
    posoutcomes = contenttasks.loc[(contenttasks['parent completed'] == True)]
    posoutcomes.to_csv("CompleteContent.csv")

    remove_old(negoutcomes, posoutcomes)

    active = contenttasks.loc[(contenttasks['parent completed'] == False)]
    children = pd.merge(active,maintasks,how="inner",left_on="parent gid",right_on="gid")
    children['AnimalID'] = children['Animal ID_y']
    children['CurrentStatus'] = children['Current Status_y']
    children['LevelReason'] = children['Level Reason_y']
    print('FCAS Asana Content Column type:')
    print(children['Level_y'].dtypes)
    children.to_csv("ContentParents.csv")

    return children

def walkdelete(duplicates):
    posoutcomes = duplicates.loc[(duplicates['parent completed'] == True)]
    list_to_delete = posoutcomes['gid']
    print(list_to_delete)
    for gid in list_to_delete:
        #print(gid)
        result = client.tasks.delete_task(gid, opt_pretty=True)
    return

def pictures(df_old,df_raw):
    pic_dict=dictionary['pictures']
    pp = pprint.PrettyPrinter(indent=2)
    xml = requests.get(pic_dict['url'])
    tree = ET.fromstring(xml.text)
    dict_of_url ={'aid':[],'url':[]}
    for child in tree:
        try:
            dict_of_url['aid'].append(child[0][0].text)
            dict_of_url['url'].append(child[0][8].text)
        except:
            print("end")
  
    df_url=pd.DataFrame.from_dict(dict_of_url)
    df_url.to_csv("url.csv")
    df_raw['AnimalNumber']=df_raw['AnimalNumber'].str[3:]
    missingpics = pd.merge(df_url,df_raw,left_on='aid',right_on='AnimalNumber',how='outer')
    missingpics.to_csv('Missing_Pictures.csv')
    df_old=df_old[pic_dict['asana_gid_df_keep']]
    df_old[pic_dict['combine_aid_right']]=df_old[pic_dict['combine_aid_right']].str[3:]
    df_url = df_url.merge(df_old,right_on=pic_dict['combine_aid_right'],left_on=pic_dict['combine_aid_left'],how='inner')
    df_url.to_csv("merg_Pict.csv")

    list_o_list=[]
    for row in df_url.itertuples(index=False):
        row_list={}
        for x in pic_dict['itercols']:
            row_list[x]=getattr(row,x)
        list_o_list.append(row_list)

    counter=0
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
    # client.tasks.update_task(row[39],{'custom_fields':options},opt_pretty=True)
        future_to_url = {executor.submit(picture_uploader,data): data for data in list_o_list}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                # new_gid['']
                print(url)
                counter+=1
                
                # print(future.result())
            except BaseException as err:
                print(err.args)
                
        # except:
            # print(row[3])
    # payload = {
    #     'LoginShelterId':'usga104',
    #     'LoginUsername':'emayfield',
    #     'LoginPassword':'L.o.t.r.12'
    # }
    # with requests.session() as s:
    #     header={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0'}
    #     cookies = s.get('https://sms.petpoint.com/sms3/forms/signinout.aspx',headers=header)
        
    #     for x in cookies.cookies:
    #         print(x)
    #     p=s.post('https://sms.petpoint.com/sms3/forms/signinout.aspx',data=payload,headers=header,cookies=cookies.cookies)
    #     print(p.status_code)
    #     pet=s.get('https://sms.petpoint.com/sms3/enhanced/animal/50963191',headers=header)
    #     soup=bs(pet.content,'html.parser')
    #     file1 = open('html.html','w')
    #     file1.write(str(soup))
    #     file1.close()
        # print(soup.find(''))
    return counter

def assigntags(dogs):
    small = dogs.loc[(dogs['AnimalWeight'] > 0) & (dogs['AnimalWeight'] < 25)]
    small.to_csv('small.csv')
    for row in small.index:
        print(small['gid'][row])
        result = client.tasks.add_tag_for_task(small['gid'][row], {'tag': '1203827915981310'}, opt_pretty=True)
    medium = dogs.loc[(dogs['AnimalWeight'] >= 25) & (dogs['AnimalWeight'] < 45)]
    medium.to_csv('medium.csv')
    for row in medium.index:
        print(medium['gid'][row])
        result = client.tasks.add_tag_for_task(medium['gid'][row], {'tag': '1203717691073440'}, opt_pretty=True)
    large = dogs.loc[(dogs['AnimalWeight'] >= 45)]
    large.to_csv('large.csv')
    for row in large.index:
        print(large['gid'][row])
        result = client.tasks.add_tag_for_task(large['gid'][row], {'tag': '1203827915981305'}, opt_pretty=True)
    return

def picture_uploader(data):
    gid = data['gid']
    name= data['AnimalName']+'.jpg'
    url=data['url']
    
    if url != dictionary['pictures']['url_fake']:
        img = urlopen(url).read()
        result = client.attachments.create_attachment_for_task(gid,file_content=img,file_name=name ,file_content_type='image/jpeg',opt_pretty=True)
    # result = client.attachments.create_attachment_for_task(gid,file_name=options['name'],url = options['url'],resource_subtype=options['resource_subtype'], opt_pretty=True)    

    return result

def client_test():
    setClientWithToken(client)
    (url, state) = client.session.authorization_url()
    print("authorized=", client.session.authorized)
    found = True
    last_date = datetime.now().isoformat()
    offset = None
    tasks = []
    tasks = client.tasks.get_tasks_for_project(dictionary['projects']['main']['gid'],{'is_subtask':False,'opt_fields' : ['custom_fields.name', 
    'custom_fields.display_value','completed', 'name', 'permalink_url', 'created_at','memberships.section.name', 
    'memberships.section.project.name' ]})
    # while found:
    #     result = client.tasks.get_tasks_for_project(dictionary['projects']['main']['gid'],{'sort_by':"created_at", 'limit':100, 'offset': offset, 'is_subtask':False,'opt_fields' : ['custom_fields.name', 'custom_fields.display_value','completed', 'name', 'permalink_url', 'created_at','memberships.section.name', 'memberships.section.project.name' ]})
    #     # 'created_at.before' : last_date,
    #     found = False
    #     for r in result:
    #         found = True
    #         last_date = r["created_at"]
    #         tasks.append(r)
    #         print(r)
    projectmap={}
    pp = pprint.PrettyPrinter(indent=2)
    column_titles = ['gid']
    gid_dict ={}
    row_df =[]
    counter =True
    
    for r in tasks:
        row_list=[r['gid']]
        len_cols = dictionary['variables']['len_cols']
        for x in r['custom_fields']:
            if(counter):
                gid_dict[x['name']]=x['gid']
                column_titles.append(x['name'])
            row_list.append(x['display_value'])
        row_list.append(r['completed'])
        temp_member_list = {}
        df_membership[r['gid']]=r['memberships']
        # print(row_list)
        # print(len(row_list))
        if(counter):
            column_titles.append("completed")
        if len(row_list)==dictionary['variables']['len_cols']:
            row_df.append(row_list)
            counter=False
        else:
            # print(row_list)
            if(counter ==True):
                column_titles=['gid']   
    print(len(column_titles))
    counter=0
    for x in row_df:
        if(len(x)>dictionary['variables']['len_cols']):           
            print(counter)
            print(row_df[counter])
            row_df.pop(counter)
        counter+=1
    df_asana_database = pd.DataFrame(row_df,columns=column_titles)
    df_asana_database.to_csv("Asana_dataframe.csv")
    return [df_asana_database,gid_dict,df_membership] 

def attachments():
    setClientWithToken(client)
    (url, state) = client.session.authorization_url()
    print("authorized=", client.session.authorized)
    tasks = client.tasks.search_tasks_for_workspace('1176075726005695', {'projects.any':'1200600287945473','has_attachment' :False, 'limit':50, 'is_subtask':False, 'opt_fields' : ['custom_fields.name', 'custom_fields.display_value', 'completed', 'name', 'permalink_url']}, opt_pretty=True)
    projectmap={}
    pp = pprint.PrettyPrinter(indent=2)
    column_titles = ['gid']
    gid_dict ={}
    row_df =[]
    counter =True
    
    for r in tasks:
        row_list=[r['gid']]
        len_cols = dictionary['variables']['len_cols']
        for x in r['custom_fields']:
            if(counter):
                gid_dict[x['name']]=x['gid']
                column_titles.append(x['name'])
            row_list.append(x['display_value'])
        row_list.append(r['completed'])
        temp_member_list = {}
        # print(row_list)
        # print(len(row_list))
        if(counter):
            column_titles.append("completed")
        if len(row_list)==dictionary['variables']['len_cols']:
            row_df.append(row_list)
            counter=False
        else:
            # print(row_list)
            if(counter ==True):
                column_titles=['gid']   
    print(len(column_titles))
    counter=0
    for x in row_df:
        if(len(x)>dictionary['variables']['len_cols']):           
            print(counter)
            print(row_df[counter])
            row_df.pop(counter)
        counter+=1
    df_asana_database = pd.DataFrame(row_df,columns=column_titles)
    df_asana_database.to_csv("Attachment_dataframe.csv")
    return [df_asana_database,gid_dict]

def credentials():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def email_getter(name,service):
    
    query = name["query"]
    for y in query:
        results = service.users().messages().list(userId='me', q=y[0]).execute()
        print(query)
        print(y[0])
        print(y[1])
        
        labels = results.get('messages', [])
        print(labels)
        if not labels:
            print('No labels found.')
        else:
            print('Labels:')
            for label in labels:
                print(labels[0]['id'])
        label = labels[0]['id']
        df=[]
        for x in labels:
            label = x['id']
            user = 'me'
            switch(service,user,label,name,y[1])
        

    return df

def switch(service,user,label,name,filename):
    attachmenttype = name["attachmenttype"]
    if attachmenttype == "inbody":
        df = getcsv(name,service,user,label)
    if attachmenttype =="attachment":
        df =GetAttachments(name,service,user,label,filename)
    return df

def GetAttachments(name,service, user_id, msg_id,filename):
    """Get and store attachment from Message with given id.

    :param service: Authorized Gmail API service instance.
    :param user_id: User's email address. The special value "me" can be used to indicate the authenticated user.
    :param msg_id: ID of Message containing attachment.
    """

    message = service.users().messages().get(userId=user_id, id=msg_id).execute()
    pp = pprint.PrettyPrinter(indent=3)
    
    with open("tempshit"+str(msg_id)+".txt","w") as f:
        f.write(pp.pformat(message))
    counter =0
    
    print(message['payload']['headers'][17]['value'])
    # filename = name['switch'][message['payload']['headers'][17]['value']]
    

    for part in message['payload']['parts']:
        print(counter)
        if part['filename']:
            if part['partId']==0:
                continue
            else:
                att_id = part['body']['attachmentId']
                att = service.users().messages().attachments().get(userId=user_id, messageId=msg_id,id=att_id).execute()
            data = att['data']
            file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
            path = part['filename']
            with open(filename,"wb") as f:
                    f.write(file_data)
            # if name["filetype"] == "excel":
            #     df = pd.read_excel(name['filename'][counter],skiprows=name["skiprows"])
            # if name["filetype"] == "csv":
            #     df = pd.read_csv(filename,skiprows=name["skiprows"])
            #     print(df.head())
            
            # df_list.append(df)  
    return

def getcsv(name,service,user,label):
    body = service.users().messages().get(userId='me',id=label,format= 'full').execute()
    try:
        try:
            decode=base64.urlsafe_b64decode(body["payload"]["parts"][0]["body"]["data"])
        except:
            decode=base64.urlsafe_b64decode(body["payload"]["body"]["data"])        
    except: 
        body = service.users().messages().attachments().get(userId='me',id=body["payload"]["parts"][1]["attachmentId"],messageId=label).execute()
        decode = base64.urlsafe_b64decode(body['data'])
    soup = bs(decode, "html.parser")
    pre = soup.find_all('p')
    data = []
    for x in range(len(pre)):
        data.append(pre[x].text.split(","))
    headers = data.pop(0)
    df = pd.DataFrame(data,columns = headers)
    

    return df

def main():
    startTime = time.time()
    
    try:
        # service = build('gmail', 'v1', credentials=credentials())
        # email_getter(dictionary['emails'],service)
        check_enum()
        lists = client_test()
        pand = pandatime()
        dfs = comb_dfs(lists[0],pand[0],lists[1])
        # tags = assigntags(dfs[0])
        # result = create_new_enum(pand[0])
        # # new_add = create_new(dfs[1])
        # out=remove_old(dfs[4],dfs[5])
        # intake_ol = bring_back_old(dfs[3]) 
        # update = update_existing(dfs[0])
        # walk = walk_df()

        # lists=client_test()
        # walkboardclean = walkclean(walk[0],lists[0])
        # #oldpathways = pathways_df()
        # #newpathways = pathways(dfs[6],oldpathways[0])
        # oldrtg = rtg_df()
        # readytogo = rtg(dfs[7],oldrtg[0])
        # oldrtf = rtf_df()
        # readytofoster = rtf(dfs[8],oldrtf[0])
        # fosdf = foster_df()
        # fos = foster(fosdf[0])
        # attach = attachments()
        # dfsa = comb_pics(attach[0],pand[0],attach[1])
        # picts = pictures(dfsa[0],pand[0])
        # content = content_df()
        # contentboardclean = contentclean(content[0],lists[0])
        # contentupdate = update_content(contentboardclean)
        # walk = walk_df()
        # walkduplicates = walkdelete(walk[0])
        # walkboardclean = walkclean(walk[0],lists[0])
        # walkupdates = update_walks(walkboardclean)
        
        executionTime = (time.time() - startTime)
        print("Completed")
        print('Execution time in seconds: ' + str(executionTime))
        print("execution time: " +str(math.floor(executionTime/60))+"m "+str(executionTime%60)+"s")
    except Exception:
        executionTime = (time.time() - startTime)
        print(traceback.format_exc())
        print("Failed")
        print('Execution time in seconds: ' + str(executionTime))
        print("execution time: " +str(math.floor(executionTime/60))+"m "+str(executionTime%60)+"s")
        
    return

if __name__=='__main__':
    main()