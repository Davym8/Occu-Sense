#sudo pip3 install Adafruit_DHT
#requirement - need DHT library 

from time import sleep
import RPi.GPIO as GPIO
import sys
import Adafruit_DHT
import requests
import json

url = "https://wap.tplinkcloud.com?token=5b2a0cda-CTWBN5xjydqNigFZK0bVONb"
on_payload = json.dumps({
    "method": "passthrough",
    "params": {
        "deviceId": "8006271D01FC0ED5250D5FBA3AF2B79B1E6452F1",
        "requestData": "{\"system\":{\"set_relay_state\":{\"state\":1}}}"
  }
})
off_payload = json.dumps({
    "method": "passthrough",
    "params": {
        "deviceId": "8006271D01FC0ED5250D5FBA3AF2B79B1E6452F1",
        "requestData": "{\"system\":{\"set_relay_state\":{\"state\":0}}}"
  }
})
headers = {'Content-Type': 'application/json'}

DHT_SENSOR = Adafruit_DHT.DHT22

GPIO.setmode(GPIO.BCM)
PIR = 16
DHT = 15

GPIO.setup(PIR,GPIO.IN)
GPIO.setup(DHT,GPIO.IN)

SET_TEMP = 24

def controlHVAC_on(tries):

    hum, temp = Adafruit_DHT.read_retry(DHT_SENSOR, DHT)
    tries = tries

    if temp is not None:
        if temp < SET_TEMP:
            r = requests.put(url, headers=headers, data=on_payload)
        elif temp > SET_TEMP:
            r = requests.put(url, headers=headers, data=off_payload)
    else:
        while tries > 0:
            sleep(1000)
            tries -= 1
            controlHVAC_on(tries)

def controlHVAC_off():

    #wait 30 seconds to confirm no motion
    i = 0
    while i < 30:
        motion = GPIO.input(PIR)
        if motion == 1:
            return
        sleep(1)
        i += 1
    r = requests.put(url, headers=headers, data=off_payload)



def main():

    try:
        #motion detected - controlHVAC_on
        GPIO.add_event_detect(PIR, GPIO.RISING, callback=lambda x: controlHVAC_on(10))
        #no motion dtected - controlHVAC_off
        GPIO.add_event_detect(PIR, GPIO.FALLING, callback=controlHVAC_off)
        while True:
            #wait for change in motion
            sleep(20)
    except KeyboardInterrupt:
        print("exit")
        sys.exit()
        GPIO.cleanup()


if __name__ == '--main__':
    main()
