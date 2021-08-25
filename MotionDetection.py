import RPi.GPIO as GPIO
import time
import requests
import sys
import requests
import json
import Adafruit_DHT


# HTTP PUT data for light
url = "http://192.168.1.114:80/api/6A69BD6601/lights/2/state"
on_payload = "{\"on\":true}"
off_payload = "{\"on\":false}"
headers = {'Content-Type':'text/plain'}

ur2 = "https://wap.tplinkcloud.com?token=5b2a0cda-CTWBN5xjydqNigFZK0bVONb"
on_payload2 = json.dumps({
    "method": "passthrough",
    "params": {
        "deviceId": "8006271D01FC0ED5250D5FBA3AF2B79B1E6452F1",
        "requestData": "{\"system\":{\"set_relay_state\":{\"state\":1}}}"
  }
})
off_payload2 = json.dumps({
    "method": "passthrough",
    "params": {
        "deviceId": "8006271D01FC0ED5250D5FBA3AF2B79B1E6452F1",
        "requestData": "{\"system\":{\"set_relay_state\":{\"state\":0}}}"
  }
})
headers = {'Content-Type': 'application/json'}


DHT_SENSOR = Adafruit_DHT.DHT22
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO_PIR_Input = 1
DHT = 15
GPIO.setup(GPIO_PIR_Input, GPIO.IN)
GPIO.setup(DHT,GPIO.IN)

SET_TEMP = 24

def controlHVAC_on():

    hum, temp = Adafruit_DHT.read_retry(DHT_SENSOR, DHT)

    if temp is not None:
        if temp < SET_TEMP - 2:
            r = requests.put(ur2, headers=headers, data=on_payload2)
        elif temp > SET_TEMP - 2:
            r = requests.put(url2, headers=headers, data=off_payload2)


while True:
  i = GPIO.input(GPIO_PIR_Input)
  
  if i == 0:  
    camera_input() #Double check with camera
    if camera_input == False:
      r = requests.put(url, headers=headers, data=off_payload) #Switch off light
      r = requests.put(url2, headers=headers, data=off_payload2) #Switch off HVAC 
      time.sleep(0.1)
    
    if camera_input == True:
      i == 1 #Continue operations
      time.sleep(0.1)
  time.sleep(0.1)
    
  if i == 1:
    r = requests.put(url, headers=headers, data=on_payload) #Switch on light
    controlHVAC_on() #Check if HVAC should be on or not
    time.sleep(0.1)

#Can use 'from gpiozero import MotionSensor'
#Allows 'pir.wait_for_motion()' and 'pir.wait_for_no_motion()'
