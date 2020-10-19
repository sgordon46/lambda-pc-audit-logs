import json
import requests
import logging
import os
import datetime

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def lambda_handler(event, context):
    
    api       = os.environ['APP_STACK']
    compute   = os.environ['COMPUTE']
    token     = os.environ['TOKEN']
    secret    = os.environ['SECRET']
    customer  = os.environ['CUSTOMER']
    sumoLogic = os.environ['SUMOLOGIC']

    #Generate a Token for access to Prisma Cloud. 
    response = requests.post(api+"/login", json={"username":token, "password":secret,"customerName":customer})
    PCtoken = response.json()['token']
    
    #Generate a Token for access to Prisma Cloud Compute. 
    response = requests.post(compute+"/api/v1/authenticate", json={"username":token, "password":secret})
    PCCtoken = response.json()['token']
    
    #Set Prisma Cloud Headers for Login with token
    pcHeaders = {
     'x-redlock-auth': PCtoken,
     'Content-Type': 'application/json',
     'Accept': 'application/json'
    }
    
    pccHeaders = {
     'Authorization': 'Bearer '+PCCtoken,
     'Accept': 'application/json'
    }
    
    #Set API query for last 5 minutes of activity - this will coincide with the Lamdba Trigger
    pcQuery="?timeType=relative&timeAmount=5&timeUnit=minute"
    
    #Request the audit events from Prisma Cloud
    r = requests.get(api+"/audit/redlock"+pcQuery, headers=pcHeaders)


    #Post each event to SumoLogic
    for i in r.json():
        if "audits" not in i['user']:
            requests.post(sumoLogic,json=i)
  
    pccQuery="?limit=20&offset=0&reverse=false"

    #Request Compute Audits
    r = requests.get(compute+"/api/v1/audits/mgmt"+pccQuery, headers=pccHeaders)
    
    for i in r.json():
        time_entry=datetime.datetime.strptime(i['time'],'%Y-%m-%dT%H:%M:%S.%fZ')
        between=datetime.datetime.now() - time_entry
        if between.seconds<300 and token not in i['username'] :
            requests.post(sumoLogic,json=i)

