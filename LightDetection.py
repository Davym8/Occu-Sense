import RPi.GPIO as GPIO
from time import sleep
import requests

# HTTP PUT data for light
url = "http://192.168.1.114:80/api/6A69BD6601/lights/2/state"
on_payload = "{\"on\":true}"
off_payload = "{\"on\":false}"
headers = {'Content-Type':'text/plain'}

class LightDetection:
    #GPIO set Mode
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    #set GPIO Pins
    PIR = 18 

    #set GPIO direction
    GPIO.setup(PIR, GPIO.IN)

    while True:
        #when motion detected turn on light
        if(GPIO.input(PIR)):
            r = requests.put(url, headers=headers, data=on_payload)
            #Time delay 10 minutes
            sleep(600)
            #Uncomment this delay for testing
            #sleep(5)
        else:
            #when no motion detected turn off light
            r = requests.put(url, headers=headers, data=off_payload)
