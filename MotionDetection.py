import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO_PIR_Input = 1
GPIO_LED2 = 3
GPIO.setup(GPIO_PIR_Input, GPIO.IN)
GPIO.setup(GPIO_LED2, GPIO.OUT)

while True:
  i = GPIO.input(GPIO_PIR_Input)
  
  if i == 0:  
    camera_input() #Double check with camera
    if camera_input == False:
      GPIO.output(GPIO_LED, GPIO.LOW) #Switch off light
      GPIO.output(GPIO_HVAC, GPIO.LOW) #Switch off HVAC 
      time.sleep(0.1)
    
    if camera_input == True:
      i == 1 #Continue operations
      time.sleep(0.1)
  time.sleep(0.1)
    
  if i == 1:
    GPIO.output(GPIO_LED, GPIO.HIGH) #Switch on light
    HVAC() #Check if HVAC should be on or not
    time.sleep(0.1)

#Can use 'from gpiozero import MotionSensor'
#Allows 'pir.wait_for_motion()' and 'pir.wait_for_no_motion()'
