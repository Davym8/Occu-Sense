import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import pickle

"""
This is the last step and the standalone file for facial recognition we will not use this program for the 
project.
this will run the camera and display the camera which will detect faces
if will give an accuracy along with the name its detecting
if multiple faces are in the image it will match them with their corresponding labels and give
accuracy data
if an unknown face is seen it will turn red. if known green

"""

with open('labels', 'rb') as f:
    dict = pickle.load(f)
    f.close()

camera = PiCamera()
camera.resolution = (1280, 1088)
camera.framerate = 42
rawCapture = PiRGBArray(camera, size=(1280, 1088))


faceCascade = cv2.CascadeClassifier("/home/pi/Desktop/FaceRec/haarcascades/haarcascade_frontalface_default.xml") # MUST CHANGE TO SUIT YOUR COMPUTER FILES
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trainer.yml")

font = cv2.FONT_HERSHEY_SIMPLEX

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    frame = frame.array
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray, scaleFactor = 1.5, minNeighbors = 5)
    for (x, y, w, h) in faces:
        roiGray = gray[y:y+h, x:x+w]

        id_, conf = recognizer.predict(roiGray)
                
        for name, value in dict.items():            
            if value == id_:
                namex = name
                print(name)                
                

        if conf <= 20:
            print("Success")
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, namex + str(conf), (x, y), font, 2, (0, 0 ,255), 2,cv2.LINE_AA)
            

        else:
            print("Failed")
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
            cv2.putText(frame, namex + str(conf), (x, y), font, 2, (0, 0 ,255), 2,cv2.LINE_AA)

    cv2.imshow('frame', frame)
    key = cv2.waitKey(1)
    rawCapture.truncate(0)

cv2.destroyAllWindows()