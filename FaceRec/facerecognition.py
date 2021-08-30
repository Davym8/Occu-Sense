import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np 
import os
import sys

"""
This file is where we start
in this file we initialise the camera and create
a directory which will make a directory for the person
we are identifying
in this system we will be using classifiers which you will need to change the 
location for the classifiers 
when running the application enter the name for the person you want to identify
then the camera will start and it will record your face
after its finished it will exit

YOU CAN CHANGE THE FRAMERATE AND RESOLUTION BUT THEY MUST MATCH
IF YOU RUN THE RESOLUTION DIFFERENTLY FROM THE MAIN SYSTEM IT WILL BE LESS ACCURATE
"""
camera = PiCamera()
camera.resolution = (1280, 1088)
camera.framerate = 42
rawCapture = PiRGBArray(camera, size=(1280, 1088))

faceCascade = cv2.CascadeClassifier("/home/pi/Desktop/FaceRec/haarcascades/haarcascade_frontalface_default.xml") #MUST CHANGE FOR YOUR OWN COMPUTER
name = input("What's his/her Name? ")
dirName = ("/home/pi/Desktop/FaceRec/images/" + name) #MUST CHANGE FOR YOUR OWN COMPUTER
print(dirName)
if not os.path.exists(dirName):
    os.makedirs(dirName)
    print("Directory Created")
else:
    print("Name already exists")
    sys.exit()
# YOU CAN CHANGE THE ACCURACY BY CHANGING THE COUNT in line 36 
# the higher it is the more accurate    
count = 1
for frame in camera.capture_continuous(rawCapture, format = "bgr", use_video_port=True):
    if count > 200:
        break
    frame = frame.array
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray, scaleFactor = 1.5, minNeighbors = 5)
    for (x, y, w, h) in faces:
        roiGray = gray[y:y+h, x:x+w]
        fileName = dirName + "/" + name + str(count) + ".jpg"
        cv2.imwrite(fileName, roiGray)
        cv2.imshow("face", roiGray)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        count += 1

    cv2.imshow('frame', frame)
    key = cv2.waitKey(1)
    rawCapture.truncate(0)

    if key == 27:
        break

cv2.destroyAllWindows()