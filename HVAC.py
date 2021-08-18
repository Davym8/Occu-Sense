#$sudo pip3 install Adafruit_DHT
#requirement - need DHT library 

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

def controlHVAC_on(tries):

	hum, temp = Adafruit_DHT.read_retry(DHT_SENSOR, DHT)
	tries = tries

	if temp is not none:
		if temp < SET_TEMP:
			GPIO.output(HVAC, GPIO.HIGH)
		elif temp > SET_TEMP:
			GPIO.output(HVAC, GPIO.LOW)

	else:
		while tries > 0:
			sleep(1000)
			tries -= 1
			controlHVAC_on(tries)
		
		#if thermometer fail, turn on hvac
		#and use hvac thermomoter	
		GPIO.output(HVAC, GPIO.HIGH)
		print('thermomoter failed - please check')




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



def main():

	try:
		#motion detected - controlHVAC_on
		GPIO.add_event_detect(PIR, GPIO.RISING, callback=lambda x: controlHVAC_on(10))
		#no motion dtected - controlHVAC_off
		GPIO.add_event_detect(PIR, GPIO.FALLING, callback=controlHVAC_off)
		
		while true:
			#wait for change in motion
			time.sleep(20)


	except KeyboardInterrupt:
		print("exit")
		sys.exit()
		GPIO.cleanup()


if __name__ == '--main__':
	main()

