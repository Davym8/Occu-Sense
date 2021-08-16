import RPi.GPIO as GPIO
import time

def LightDetection():
 
 #GPIO set Mode
 GPIO.setwarnings(False)
 GPIO.setmode(GPIO.BCM)

 #set GPIO Pins
 GPIO_TRIGGER = 18 
 GPIO_LED = 24

 #set GPIO direction
 GPIO.setup(GPIO_TRIGGER, GPIO.IN)
 GPIO.setup(GPIO_LED, GPIO.OUT)
 GPIO.output(GPIO_LED, GPIO.LOW)

 while True:
 #when motion detected turn on LED
     if(GPIO.input(PIR_input)):
         GPIO.output(LED, GPIO.HIGH)
         #Time delay 10 minutes
         time.sleep(600)
     else:
         GPIO.output(LED, GPIO.LOW)
