"""
This is the Main file which we will be using to run both functions

first we need to import the modules and files we will be using 
"""
import cv2
import sys
from picamera.array import PiRGBArray
from picamera import PiCamera
from flask import Flask, render_template, Response
from cameras import VideoCamera
from flask_basicauth import BasicAuth
from mail import sendEmail
import pickle
import time
import threading
import requests
"""
Then we will define our global variables for use

last_epoch is for calculating the time and acts as a timer for the email
email interval is for the rate of emailes we want to receive in that time
bus sets the bust devices we are using which is 1
argon address is the slave we are connecting to

positive and negative ident are booleans which will indicate whether we have
a good facial identification 

YOU CAN CHANGE THE FRAMERATE AND RESOLUTION BUT THEY MUST MATCH
IF YOU RUN THE RESOLUTION DIFFERENTLY FROM THE FACE RECOGNITION FILE IT WILL BE LESS ACCURATE
"""
last_epochs = 0.0
email_interval = 120



#Runs webserver and object/face reocgnition, using the classifiers below,
#we initialise the video camera by calling it then setup the flask server using app and credentials

    
#checks for objects and sends an email of the frame when object is detected

   
                
#called if the person is known and sends an email MUST CREATE IFTTT APPLET FOR THIS


#this function initialises the facial recognition detecing if the person is known or unknown
def livestream():
    video_camera = VideoCamera() # creates a camera object
    object_classifier = cv2.CascadeClassifier("/home/pi/Desktop/FaceRec/haarcascades/haarcascade_upperbody.xml") #opencv classifiers 
    face_classifier = cv2.CascadeClassifier("/home/pi/Desktop/FaceRec/haarcascades/haarcascade_frontalface_default.xml") # CHANGE LOCATION to where you have these 
    
    #this is for the flask server you can change the username and password to what u want
    # App Globals (do not edit)
    app = Flask(__name__)
    app.config['BASIC_AUTH_USERNAME'] = 'd'
    app.config['BASIC_AUTH_PASSWORD'] = 's'
    app.config['BASIC_AUTH_FORCE'] = True
    basic_auth = BasicAuth(app)
    last_epoch = 0.0
    start = time.time()
    
    def check_for_objects():
        last_epoch = 0.0
        email_update_interval = 120
        try:
            while True:
                frame, found_obj = video_camera.get_object(object_classifier)
                frames, found_face = video_camera.get_object(face_classifier)
                
        except:
            print (("Error sending email: "), sys.exc_info()[0])
    
    
    #this shows the route of the app and returns the index html file which will be used for creating a webpage with the video stream
    
    @app.route('/')
    @basic_auth.required
    def index():
        return render_template('index.html')

    def gen(camera):
        while True:
            frame = camera.get_frame()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            
    @app.route('/video_feed')
    def video_feed():
        return Response(gen(video_camera),
                mimetype='multipart/x-mixed-replace; boundary=frame')
        
    #this initialises the functions while continuing the other with threads
    #the flask app will not shut down unless manually shut or a sig is used
    if __name__ == '__main__':   
        t = threading.Thread(target=check_for_objects, args=())
        t.daemon = True
        t.start()
        app.run(host='0.0.0.0', debug=False, threaded=True)

def FaceRec():
    start_time = time.time()
    with open('labels', 'rb') as f:
        dict = pickle.load(f)
        f.close()    
    cameran = PiCamera()
    cameran.resolution = (1280, 1088) #you can change the resolution and framerate but they have to match
    cameran.framerate = 42
    rawCapture = PiRGBArray(cameran, size = (1280, 1088))
    positivecount = 0
    negativecount = 0
    
    faceCascade = cv2.CascadeClassifier("/home/pi/Desktop/FaceRec/haarcascades/haarcascade_frontalface_default.xml")
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("trainer.yml")
    font = cv2.FONT_HERSHEY_SIMPLEX
    #loops continuously via picam to analyse faces and give an accuracy rate
    for framed in cameran.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        framed = framed.array
        gray = cv2.cvtColor(framed, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, scaleFactor = 1.5, minNeighbors = 5)
        for (x, y, w, h) in faces:
            roiGray = gray[y:y+h, x:x+w]
            
            id_, conf = recognizer.predict(roiGray)
            #stores data as dicionary and uses recogniser to predict based on the labels and trainer                  
            for name, value in dict.items():            
                if value == id_:
                    namex = name
                    print(name)
            #the lower it is the more accurate it is
            if conf <= 20:
                print("Success")
                cv2.rectangle(framed, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(framed, namex + str(conf), (x, y), font, 2, (0, 0 ,255), 2,cv2.LINE_AA)  #will create green box and give accuracy reading      
                
                    
                    
                    #counts the positive matches to improve accuracy and when reached activates functions    
            else:
                print("Failed")
                cv2.rectangle(framed, (x, y), (x+w, y+h), (0, 0, 255), 2)
                cv2.putText(framed, namex + str(conf), (x, y), font, 2, (0, 0 ,255), 2,cv2.LINE_AA) #will create red box and give accuracy reading
                
                
        cv2.imshow('framed', framed)
        key = cv2.waitKey(1)
        rawCapture.truncate(0)
        if Negative_Ident:
            cameran.close()
            break
        elif time.time() - start_time > 120:
            cameran.close()
            break
    #will pop up warning but it doesnt matter just ignore it
        elif Positive_Ident:
            cameran.close()
            break
    cv2.destroyAllWindows()

#here is where the function breaks 
#if it has detected a good or bad match 
#depending on which it will activate another function


#these definitions are used to communicate with 
#the argon device
#by sending bits back and reading the argons reply
    

try:
    while True:
        livestream()# this will start the stream and another recog system
except KeyboardInterrupt:    
    exit()
