import requests
import config
import asana
import pandas as pd

client = asana.Client.access_token(config.token)
client.headers={"asana-enable": "new_user_task_lists"}

def setClientWithToken(clientjson):
    global client 
    client = clientjson

setClientWithToken(client)

email = 'clarespecht21@gmail.com'
result = client.users.get_users_for_workspace('1176075726005695',{'opt_fields' : ['email']}, opt_pretty=True)
userlist = []
for r in result:
    userlist.append(r)
result = list(filter(lambda person: person['email'] == email, userlist))
print(result[0]['gid'])