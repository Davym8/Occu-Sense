#$sudo pip3 install Adafruit_DHT
#reguirement - need DHT library 

from time import sleep
import RPi.GPIO as GPIO
import sys
import Adafruit_DHT

DHT_SENSOR = Adafruit_DHT.DHT22

GPIO.setmode(GPIO.BCM)
PIR = 17
DHT = 27
#using HVAC as pinout atm. 
#Maybe want to use remote activation instead?

HVAC = 22
GPIO.setup(PIR,GPIO.IN)
GPIO.setup(DHT,GPIO.IN)
GPIO.setup(HVAC,GPIO.OUT)

SET_TEMP = 24

def controlHVAC_on():

	#ToDO - what if sensor fail, need default
	hum, temp = Adafruit_DHT.read_retry(DHT_SENSOR, DHT)
	
	if temp is not none:
		if temp < SET_TEMP:
			GPIO.output(HVAC, GPIO.HIGH)
		elif temp > SET_TEMP:
			GPIO.output(HVAC, GPIO.LOW)

def controlHVAC_off():

	#wait 30 seconds to confirm no motion
	i = 0
	while i < 30:
		motion = GPIO.input(PIR)
		if motion == 1:
			return

		time.sleep(1)
		i += 1

	GPIO.output(HVAC, GPIO.LOW)




try:
	#motion detected - controlHVAC_on
	GPIO.add_event_detect(PIR, GPIO.RISING, callback=controlHVAC_on)
	#no motion dtected - controlHVAC_off
	GPIO.add_event_detect(PIR, GPIO.FALLING, callback=controlHVAC)
	
	while true:
		#wait for change in motion
		time.sleep(20)


except KeyboardInterrupt:
	print("exit")
	sys.exit()
	GPIO.cleanup()


