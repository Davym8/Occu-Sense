#use this to install
#python -m pip install requests
#python -m pip install pymongo
#python -m pip install pymongo[srv]

import json
import requests
import time
from pymongo import MongoClient

# Address and setup of Mongo DB
URI = "mongodb+srv://dylan:nph*wtz*ZGU8mup5exb@occusense.zfntf.mongodb.net/websitedata?retryWrites=true&w=majority"
client = MongoClient(URI)
db = client.controller
devicestates = db.devicestates

# HTTP PUT data for light
light_url = "http://192.168.1.114:80/api/6A69BD6601/lights/2/state"
light_on_pl = "{\"on\":true}"
light_off_pl = "{\"on\":false}"
light_headers = {'Content-Type':'text/plain'}

# Light control functions
def light_on():
    r = requests.put(light_url, headers=light_headers, data=light_on_pl)
    
def light_off():
    r = requests.put(light_url, headers=light_headers, data=light_off_pl)

# HTTP PUT data for HVAC smart plug
hvac_url = "https://wap.tplinkcloud.com?token=5b2a0cda-CTWBN5xjydqNigFZK0bVONb"
hvac_headers = {'Content-Type': 'application/json'}
hvac_on_pl = json.dumps({
        "method": "passthrough",
        "params": {
            "deviceId": "8006271D01FC0ED5250D5FBA3AF2B79B1E6452F1",
            "requestData": "{\"system\":{\"set_relay_state\":{\"state\":1}}}"
        }
    })

hvac_off_pl = json.dumps({
        "method": "passthrough",
        "params": {
            "deviceId": "8006271D01FC0ED5250D5FBA3AF2B79B1E6452F1",
            "requestData": "{\"system\":{\"set_relay_state\":{\"state\":0}}}"
        }
    })

# HVAC smart plug control functions
def hvac_on():
    r = requests.put(hvac_url, headers=hvac_headers, data=hvac_on_pl)

def hvac_off():
    r = requests.put(hvac_url, headers=hvac_headers, data=hvac_off_pl)


# Loop to poll database for triggers to turn light on/off
while True:
    light_state = devicestates.find_one(
    { "type": "light" },
    {  "_id": 0, "state": 1 }
    ).get('state')
    
    if light_state == 1:
        light_on()
    elif light_state == 0:
        light_off()
        
    hvac_state = devicestates.find_one(
    { "type": "hvac" },
    {  "_id": 0, "state": 1 }
    ).get('state')
    
    if hvac_state == 1:
        hvac_on()
    elif hvac_state == 0:
        hvac_off()