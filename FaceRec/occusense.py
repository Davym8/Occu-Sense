"""
This is the Main file which we will be using to run both functions

first we need to import the modules and files we will be using 
"""
import cv2
import sys
import RPi.GPIO as GPIO
import Adafruit_DHT
from picamera.array import PiRGBArray
from picamera import PiCamera
from flask import *
from cameras import VideoCamera
from flask_basicauth import BasicAuth
from mail import sendEmail
import pickle
import time
import threading
import requests
from pymongo import MongoClient

#authentication to access website
username = 'admin'
pwd = 'pwd'
genCam = True

last_epochs = 0.0
email_interval = 120

Positive_Ident = False
Negative_Ident = False

#sensor variables and setup
###############################
DHT_SENSOR = Adafruit_DHT.DHT22
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO_PIR_Input = 4
DHT = 15
GPIO.setup(GPIO_PIR_Input, GPIO.IN)
GPIO.setup(DHT,GPIO.IN)

SET_TEMP = 24
light = False
hvac = False
###############################
#DataBase variables
################################
URI = "mongodb+srv://dylan:nph*wtz*ZGU8mup5exb@occusense.zfntf.mongodb.net/websitedata?retryWrites=true&w=majority"
client = MongoClient(URI)
db = client.controller
devicestates = db.devicestates

def livestream():
    object_classifier = cv2.CascadeClassifier("/home/pi/Desktop/FaceRec/haarcascades/haarcascade_upperbody.xml") #opencv classifiers 
    face_classifier = cv2.CascadeClassifier("/home/pi/Desktop/FaceRec/haarcascades/haarcascade_frontalface_default.xml") # CHANGE LOCATION to where you have these 
    
    video_camera = VideoCamera() # creates a camera object
    app = Flask(__name__)
    app.config['BASIC_AUTH_USERNAME'] = 'admin'
    app.config['BASIC_AUTH_PASSWORD'] = 'pwd'
    app.config['BASIC_AUTH_FORCE'] = True
    app.secret_key = 'hello'
    basic_auth = BasicAuth(app)
    last_epoch = 0.0
    start = time.time()
            
    #checks for objects and sends an email of the frame when object is detected variables are set for testing change as desired
    def check_for_objects():
        #timer settings
        last_epoch = 0.0
        pir_last_epoch = 0.0
        pir_interval = 120
        update_interval = 1
        detection = 0
        timeout = 120
        timeout_start = time.time()
        flag = True
        try:
            while True:
                pirinput = GPIO.input(GPIO_PIR_Input)                
                if pirinput == 0:
                    print("nothing detected", pirinput)   
                    frame, found_obj = video_camera.get_object(object_classifier)
                    frames, found_face = video_camera.get_object(face_classifier)                    
                    if found_face and (time.time() - pir_last_epoch) < pir_interval:                            
                        print("No PIR detect, Human detected")
                        pir_last_epoch = time.time()
                        continue
                    elif (time.time() - pir_last_epoch) > pir_interval:
                        pir_last_epoch = time.time()
                        print('Lights off')
                        flag = True
                        devicestates.update_one({ "type": "hvac" },{ "$set": { "state" : 0 } } )
                        devicestates.update_one( { "type": "light" }, { "$set": { "state" : 0 } } )                                                              
                elif pirinput == 1:
                    timeout_start = time.time()
                    while time.time() < timeout_start+timeout:
                        print("entered facerec")            
                        frame, found_obj = video_camera.get_object(object_classifier)
                        frames, found_face = video_camera.get_object(face_classifier) 
                        hum, temp = Adafruit_DHT.read_retry(DHT_SENSOR, DHT)                            
                        if found_face and (time.time() - last_epoch) > update_interval:
                            last_epoch = time.time()
                            print("detected face",detection)                            
                            detection += 1
                            if temp < SET_TEMP:
                                devicestates.update_one({ "type": "hvac" },{ "$set": { "state" : 1 } } )
                            if flag == True:
                                devicestates.update_one( { "type": "light" }, { "$set": { "state" : 1 } } )
                                flag = False
                        if detection == 10:
                            print ("Sending email...")
                            sendEmail(frames)
                            print("Email Sent")
                            detection = 0
                    detection = 0
                    continue                
        except:
            print (("Error sending email: "), sys.exc_info()[0])
    #flask routes for website access
    @app.route("/")
    @basic_auth.required
    def index():
        return render_template('index.html')
    
    @app.route("/", methods = ['POST', 'GET'])
    def form_processing():
        if request.method == "POST":
            button = request.form["formdata"]
            if button == 'Submit Shutdown':
                usrinput = request.form['usr']
                usrpassword = request.form['pwd']
                if usrinput != username:
                    flash("Error: username or password is incorrect")
                    return redirect(url_for('index'))
                if usrpassword != pwd:
                    flash("Error: username or password is incorrect")
                    return redirect(url_for('index')) 
                print("Server is shutting down")
                shutdown = request.environ.get('werkzeug.server.shutdown')
                if shutdown is None:
                    raise RuntimeError("Error Shutdown failed")
                else:
                    shutdown()
                    return redirect(url_for('shutdown'))
                
            elif button == 'Submit':
                light = True
                hvac = True
                print("hello")
                #ToDo need to send selection back to web to display current state
                checklight = request.form.get('aclight')
                checkheater = request.form.get('acheater')
                checkaircon = request.form.get('acair')            
                ##########
                getLight = devicestates.find_one({ "type": "light" },{  "_id": 0, "state": 1 }).get('state')
                print(getLight)
                print(checklight)
                if checklight == 'true' and getLight == 0:
                    #set device to action
                    print("Turning on light")
                    devicestates.update_one( { "type": "light" }, { "$set": { "state" : 1 } })
                    lights = True

                elif checklight == None and getLight == 1:
                    #set device to action
                    print("Turning off light")
                    devicestates.update_one({ "type": "light" },{ "$set": { "state" : 0 } })
                    lights = False

                getHvac = devicestates.find_one({ "type": "hvac" },{  "_id": 0, "state": 1 }).get('state')

                if (checkheater == 'true' or checkaircon == 'true') and getHvac == 0:
                    #set device to action
                    print("Turning on HVAC")
                    devicestates.update_one({ "type": "hvac" },{ "$set": { "state" : 1 } })
                    hvac = True

                elif (checkheater == None or checkaircon == None) and getHvac == 1:
                    #set device to action
                    print("Turning off HVAC")
                    devicestates.update_one({ "type": "hvac" }, { "$set": { "state" : 0 } })
                    hvac = False

                #returnData = {'lights'  : lights,'hvac'  : hvac}
                return render_template('index.html')                   
            else:
                return render_template('index.html')
    #camera feed
    def gen(camera):
        while genCam:
            frame = camera.get_frame()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    #returning camera feed to webpage       
    @app.route('/video_feed')
    def video_feed():
        return Response(gen(video_camera),mimetype='multipart/x-mixed-replace; boundary=frame')
    
    @app.route("/shutdown")
    def shutdown():
        return render_template('shutdown.html')
    
    @app.route("/autherror")
    def auth():
        flash("Error: username or password is incorrect")
        return redirect(url_for("/"))
            
      
    #this initialises the functions while continuing the other with threads
    #the flask app will not shut down unless manually shut or a sig is used
    if __name__ == '__main__':   
        t = threading.Thread(target=check_for_objects, args=())
        t.daemon = True
        t.start()
        app.run(host='127.0.0.1', port = 8000, debug=False, threaded=True)                 
try:
    while True:
      livestream()# this will start the stream and another recog system
except KeyboardInterrupt:    
    exit()

