import RPi.GPIO as GPIO
import time
import requests
import sys
import requests
import json
import Adafruit_DHT


ur2 = "https://wap.tplinkcloud.com?token=5b2a0cda-CTWBN5xjydqNigFZK0bVONb"
headers = {'Content-Type': 'application/json'}


DHT_SENSOR = Adafruit_DHT.DHT22
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO_PIR_Input = 7
DHT = 15
GPIO.setup(GPIO_PIR_Input, GPIO.IN)
GPIO.setup(DHT,GPIO.IN)

SET_TEMP = 24



def HVAC_on():
    on_payload2 = json.dumps({
        "method": "passthrough",
        "params": {
            "deviceId": "8006271D01FC0ED5250D5FBA3AF2B79B1E6452F1",
            "requestData": "{\"system\":{\"set_relay_state\":{\"state\":1}}}"
        }
    })
    hum, temp = Adafruit_DHT.read_retry(DHT_SENSOR, DHT)
    

    if temp is not None:
        if temp < SET_TEMP - 2:
            r = requests.put(ur2, headers=headers, data=on_payload2)
            print("HVAC is on")
            print("Target: {} and actual is {}, with the range allowed being 2 Degrees".format(SET_TEMP, temp))
            print()
        elif temp > SET_TEMP + 2:
            r = requests.put(url2, headers=headers, data=off_payload2)
            print("HVAC is off")
            print("Target: {} and actual is {}, with the range allowed being 2 Degrees".format(SET_TEMP, temp))
            print()

def HVAC_off():
    off_payload2 = json.dumps({
        "method": "passthrough",
        "params": {
            "deviceId": "8006271D01FC0ED5250D5FBA3AF2B79B1E6452F1",
            "requestData": "{\"system\":{\"set_relay_state\":{\"state\":0}}}"
        }
    })
    r = requests.put(url2, headers=headers, data=off_payload2)

def light_on():
    # HTTP PUT data for light
    url = "http://192.168.1.114:80/api/6A69BD6601/lights/2/state"
    on_payload = "{\"on\":true}"
    off_payload = "{\"on\":false}"
    headers = {'Content-Type':'text/plain'}
    r = requests.put(url, headers=headers, data=on_payload)
    
def light_off():
    r = requests.put(url, headers=headers, data=off_payload)



while True:
  i = GPIO.input(GPIO_PIR_Input)
  if i == 0:
    light_off() #Switch off light
    print("light is off")
    HVAC_off() #Switch off HVAC
    print("HVAC is off")
    print()
    time.sleep(5)
    
  time.sleep(0.1)
    
  if i == 1:
    light_on() #Switch on light
    print("light is on")
    HVAC_on() #Check if HVAC should be on or not
    time.sleep(15)
