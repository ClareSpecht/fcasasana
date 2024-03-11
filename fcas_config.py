def dictionary():
    py={ "projects":{
            'new_pet_list':['1202865592279947','1200600287945473'],
            "main":{
                'gid':"1200600287945473",
                'sections': {  
                    'Featured': '1206386867201902',
                    '0': '1206386867201903',
                    '3': '1206386867201907',
                    '4': '1206386867201906',
                    '5': '1206386867201905',
                    '6': '1206386867201904',
                    'CW': '1206386867201908',
                    'ISO': '1206386867201909',
                    'Other': '1206386867201910',
                    "Foster":"1206386867201911",
                    "Completed":"1206386867201912"
                },
            },
            "walk":{
                "gid" : "1202026739375143",
                "sections":{
                    'Featured':'1202026739375144',
                    '0':'1202026739375148',
                    '6':'1202026739375149',
                    '5' : '1202036717268960',
                    '4' : '1202037852728245',
                    '3' : '1203768970242887',
                    'CW' : '1203768970242888',
                    'ISO' : '1206569861595742',
                    'Q' : '1206105920902578',
                    'Other' : '1202037852728246',
                    'Foster' : '1203768970242889'
                },
            },
            "content":{
                "gid" : "1203684021953147"
            },
            "pathways":{
                "gid" : "1201695715366140"
            },
            "rtg":{
                "gid" : "1202594804488369",
                "sections":{
                    'Featured':'1202594804488387',
                    '0':'1202594804488388',
                    '4' : '1202594804488384',
                    '3' : '1202594804488374',
                    '5' : '1202594804488383',
                    '6' : '1202594804488389',
                    'Other' : '1202594804488370',
                    'Foster' : '1202594804488375'
                },
            },
            "rtf":{
                "gid" : "1206672116851591",
                "sections":{
                    'Featured':'1206672116851592',
                    '0':'1206672116851596',
                    '4' : '1206672116851598',
                    '3' : '1206672116851597',
                    '5' : '1206672116851599',
                    '6' : '1206672116851600',
                    'Other' : '1206672116851601',
                    'Foster' : '1206672116851602'
                },
            },
            "foster":{
                "gid" : "1201449344168303",
                "sections":{
                    'A':'1201449344168308',
                    'B':'1201449344168308',
                    'C':'1201449344168308',
                    'D' : '1201449344168308',
                    'E' : '1201449344168309',
                    'F' : '1201449344168309',
                    'G' : '1201449344168309',
                    'H' : '1201449344168309',
                    'I' : '1201449344168310',
                    'J' : '1201449344168310',
                    'K' : '1201449344168310',
                    'L' : '1201449344168310',
                    'M' : '1201449344168311',
                    'N' : '1201449344168311',
                    'O' : '1201449344168311',
                    'P' : '1201449344168311',
                    'Q' : '1201449344168312',
                    'R' : '1201449344168312',
                    'S' : '1201449344168312',
                    'T' : '1201449344168312',
                    'U' : '1201449344168313',
                    'V' : '1201449344168313',
                    'W' : '1201449344168313',
                    'X' : '1201449344168313',
                    'Y' : '1201449344168313',
                    'Z' : '1201449344168313',
                    'LEF' : '1201449344168314'
                },
            },
        },
        "variables":{
            'len_cols':33,
            'lenwname':34,
            'len_walk':35
        },
        # 'emails':{ 
        #     "query":[["from:PetPoint Reporting Scheduler  subject: 'Daily Inventory asana' newer_than:1d ",'Current Inv.csv'],['from:PetPoint Reporting Scheduler  subject: "DCAS HW Asana" newer_than:1d ','HW result.csv']],
        #     # "query":[["from:PetPoint Reporting Scheduler  subject: 'Daily Inventory asana' newer_than:4h ",'Current Inv.csv'],['from:PetPoint Reporting Scheduler  subject: "DCAS HW Asana" newer_than:4h ','HW result.csv']],
        #     "attachmenttype":"attachment",
        #     "filename":["Current inv.csv","HW Results.csv","foster.csv","outcome.csv"],
        #     "filetype":"csv",
        #     "skiprows":2,
        #     'switch':{'Daily Inventory asana':'Current Inv.csv','DCAS Daily hw':'HW result.csv'}
        # },

        'create_new':{
            "new_remove":['AnimalName',"projects"],
            "df_switch":{
                        'AnimalNumber': "Animal ID",
                        'Stage':"Current Status", 'DateOfBirth':"DOB", 'ARN':'Level Reason', 'ColorAndBreed':'Color & Breed', 'ExpirationDate':'Rabies Revaccination Date',
                        'AnimalWeight':"Weight", 'Result':"HW", 'FosterReason':'Foster Start Reason', 'HoldReason': 'Hold', 'MicrochipNumber':'Microchip ID',
                        "DogTest":"\"Dog Test\" Notes", "Behavior":"Behavior Notes", 'HomeNotes':"Foster/Home Notes", 'ShortURL':'Short URL'
                        },
            "df_fields_keep":[
                'AnimalNumber', 'AnimalName',  'Age', 'ARN', 'ColorAndBreed',
                'Location', 'DateOfBirth', 'Stage', 'ShortURL', 'ExpirationDate',
                'AnimalWeight', 'Level', 'Sex', 'MicrochipNumber',
                "IntakeDate", 'Result', 'FosterReason', 'HoldReason'
            ]
            },
        "update_existing":{
            'update_fields':['AnimalWeight','Age_x', 'ColorAndBreed','ShortURL','MicrochipNumber','ExpirationDate','ARN', 'Location_x', 'Stage', 'Level_x', 'Sex_x', 'Result','FosterReason','HoldReason','DogTest','Behavior','HomeNotes'],
            'df_fields_keep':['gid','AnimalWeight','Age_x','ColorAndBreed','ShortURL','MicrochipNumber','ExpirationDate','ARN','Location_x','AnimalName', 'Stage', 'FosterReason', 'HoldReason', 'Level_x', 'Sex_x', 'Result','DogTest','Behavior','HomeNotes'],
            "df_switch":{ 
                    'AnimalNumber': "Animal ID", 'ColorAndBreed':'Color & Breed',
                    'DateOfBirth':"DOB", 'MicrochipNumber':'Microchip ID', 'ExpirationDate':'Rabies Revaccination Date',
                    'AnimalWeight':"Weight", "Age_x":"Age", 'ARN':'Level Reason',
                    "Location_x":"Location", "Level_x":"Level", 'ShortURL':'Short URL',
                    'Stage' : 'Current Status', 'Sex_x' : 'Sex', 'Result':"HW", 'FosterReason':'Foster Start Reason', 'HoldReason':'Hold',
                    "DogTest":"\"Dog Test\" Notes", "Behavior":"Behavior Notes", 'HomeNotes':"Foster/Home Notes"
                    },
            'name_switch':{

            }
        },     
        "update_walks":{
            'update_fields':['Weight_y','Age_y','LevelReason','Location_y', 'CurrentStatus', 'Level_y', 'Sex_y', 'AnimalID', 'HW_y'],
            'df_fields_keep':['gid_x','Weight_y','Age_y','LevelReason','Location_y', 'CurrentStatus', 'Level_y', 'Sex_y', 'AnimalID', 'HW_y'],
            "df_switch":{ 
                    'AnimalID': "Animal ID",
                    'Weight_y':"Weight", "Age_y":"Age", 'LevelReason':'Level Reason',
                    "Location_y":"Location", "Level_y":"Level",
                    'CurrentStatus' : 'Current Status', 'Sex_y' : 'Sex', 'HW_y' : 'HW'
                    },
            'name_switch':{

            }
        },            
        "pictures":{
            'url':"http://ws.petango.com/webservices/wsadoption.asmx/AdoptableSearch?authKey=i20ehcbq1onr5q43bdp1p8xb17ooc3mbkxqugetdwwu857dffu&speciesID=&sex=&ageGroup=&location=&site=&onHold=&orderBy=&primaryBreed=&secondaryBreed=&specialNeeds=&noDogs=&noCats=&noKids=&stageID=",
            'asana_gid_df_keep':['gid', 'AnimalNumber','Animal ID','AnimalName'],
            'combine_aid_right':'AnimalNumber',
            'combine_aid_left':'aid',
            'url_fake':'https://g.petango.com/shared/Photo-Not-Available-dog.gif',
            'gid_content':"",
            'itercols':['gid','url', 'AnimalNumber','AnimalName'],
            },
         "remove_old":{
            'df_fields_keep':'gid'
         },
         "bring_back_old":{
           'df_fields_keep':'gid' 
         },
         "enum":{
            "df_fields_keep":["Stage","HoldReason", "FosterReason"],
            'df_switch':{
                "Stage":"Current Status",
                "HoldReason" : "Hold",
                'FosterReason':'Foster Start Reason'
            }
         },
        "fields":""
        
    }
    return py