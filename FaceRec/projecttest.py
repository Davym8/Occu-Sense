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
import pickle
import time
import threading
import requests
from pymongo import MongoClient

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

#Light and HVAC url, headers and payloads
#####################################################
light_url = "http://192.168.1.114:80/api/6A69BD6601/lights/2/state"
light_headers = {'Content-Type':'text/plain'}
light_on_payload = "{\"on\":true}"
light_off_payload = "{\"on\":false}"

hvac_url = "https://wap.tplinkcloud.com?token=5b2a0cda-CTWBN5xjydqNigFZK0bVONb"
hvac_check_payload = json.dumps({"method": "passthrough","params": {"deviceId": "8006271D01FC0ED5250D5FBA3AF2B79B1E6452F1","requestData": "{\"emeter\":{\"get_realtime\":{}}}"}})
hvac_headers = {'Content-Type': 'application/json'}
hvac_on_payload = json.dumps({ "method": "passthrough", "params": { "deviceId": "8006271D01FC0ED5250D5FBA3AF2B79B1E6452F1", "requestData": "{\"system\":{\"set_relay_state\":{\"state\":1}}}" } })
hvac_off_payload = json.dumps({  "method": "passthrough",   "params": { "deviceId": "8006271D01FC0ED5250D5FBA3AF2B79B1E6452F1",   "requestData": "{\"system\":{\"set_relay_state\":{\"state\":0}}}"    } })
######################################################

#DB variables
################################

URI = 
client = MongoClient(URI)
db = client.controller
devicestates = db.devicestates

################################

# on commands
# devicestates.update_one(
#   { "type": "hvac" },
#   { "$set": { "state" : 1 } }
# )
# devicestates.update_one(
#   { "type": "light" },
#   { "$set": { "state" : 1 } }
# )

# off commands
# devicestates.update_one(
#   { "type": "hvac" },
#   { "$set": { "state" : 0 } }
# )
# devicestates.update_one(
#   { "type": "light" },
#   { "$set": { "state" : 0 } }
# )

# result = devicestates.find_one(
#     { "type": "light" },
#     {  "_id": 0, "state": 1 }
#     ).get('state')


def livestream():
    object_classifier = cv2.CascadeClassifier("/home/pi/Desktop/FaceRec/haarcascades/haarcascade_upperbody.xml") #opencv classifiers 
    face_classifier = cv2.CascadeClassifier("/home/pi/Desktop/FaceRec/haarcascades/haarcascade_frontalface_default.xml") # CHANGE LOCATION to where you have these 
    
    video_camera = VideoCamera() # creates a camera object
    
    
    app = Flask(__name__)
    app.config['BASIC_AUTH_USERNAME'] = 'd'
    app.config['BASIC_AUTH_PASSWORD'] = 's'
    app.config['BASIC_AUTH_FORCE'] = True
    app.secret_key = 'hello'
    basic_auth = BasicAuth(app)
    last_epoch = 0.0
    start = time.time()
            
#checks for objects and sends an email of the frame when object is detected
    def check_for_objects():        
        last_epoch = 0.0
        pir_last_epoch = 0.0
        pir_interval = 1
        update_interval = 30
        detection = 0
        flag = True
        try:

            while True:

                pirinput = GPIO.input(GPIO_PIR_Input)
                
                if pirinput == 0:
                    print("Nothing detected,PIR")
                    while (time.time() - last_epoch) < update_interval:
                        
                        frame, found_obj = video_camera.get_object(object_classifier)
                        frames, found_face = video_camera.get_object(face_classifier)
                        last_epoch = time.time()

                        if found_obj and (time.time() - last_epoch) > update_interval:
                            last_epoch = time.time()
                            print("No PIR detect, camera detect")
                            continue
                        else:
                            print('Lights off')
                            flag = True
                            devicestates.update_one(
                               { "type": "hvac" },
                               { "$set": { "state" : 0 } }
                            )
                            devicestates.update_one(
                               { "type": "light" },
                               { "$set": { "state" : 0 } }
                            )
                                                        
                    
                if pirinput == 1:

                    while detection < 10:
                        
                        print("detected",detection)
                        frame, found_obj = video_camera.get_object(object_classifier)
                        frames, found_face = video_camera.get_object(face_classifier)
                        
                        if flag== True:
                            devicestates.update_one(
                               { "type": "hvac" },
                               { "$set": { "state" : 1 } }
                            )
                            devicestates.update_one(
                               { "type": "light" },
                               { "$set": { "state" : 1 } }
                            )
                            flag = False

                        if found_obj and (time.time() - last_epoch) > update_interval:
                            last_epoch = time.time()
                            #or turn on here, but 30 sec delay
                            #turn on lights+HVAC
                            detection += 1
                            print(detection)
                            
                    #not sure if we are sending email for this?
                    #sendEmail(frame)
                    detection = 0   
                
                
        except:
            print (("Error sending email: "), sys.exc_info()[0])
    
    
    @app.route("/")
    @basic_auth.required
    def index():
        return render_template('index.html')
    
    @app.route("/", methods = ['POST', 'GET'])
    def shutdown_server():
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
                print("hello")
                #ToDo need to send selection back to web to display current state
                check = request.form.get('check')
                checked = request.form.get('checked')
                checkers = request.form.get('checkers')
                print(check,checked,checkers)
                ##########
                getLight = devicestates.find_one({ "type": "light" },{  "_id": 0, "state": 1 }).get('state')
                
                
                if check == 'true' and getLight == 0:
                    #set device to action
                    devicestates.update_one(
                               { "type": "light" },
                               { "$set": { "state" : 1 } }
                            )
                    lights = True

                elif check == 'None' and getLight == 1:
                    #set device to action
                    devicestates.update_one(
                               { "type": "light" },
                               { "$set": { "state" : 0 } }
                            )
                    lights = False

                getHvac = devicestates.find_one({ "type": "hvac" },{  "_id": 0, "state": 1 }).get('state')

                if (checked == 'true' or checkers == 'true') and getHvac == 0:
                    #set device to action
                    devicestates.update_one(
                               { "type": "hvac" },
                               { "$set": { "state" : 1 } }
                            )
                    hvac = True

                elif (checked == 'None' or checkers == 'None') and getHvac == 1:
                    #set device to action
                    devicestates.update_one(
                               { "type": "hvac" },
                               { "$set": { "state" : 0 } }
                            )
                    hvac = False

                returnData = {'lights'  : lights,'hvac'  : hvac}
                return render_template('index.html', **returnData) 
                  
            else:
                return render_template('index.html')
    
    '''
    @app.route("/", methods = ['POST', 'GET'])
    def shutdown_server():
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
                print("hello")
                #ToDo need to send selection back to web to display current state
                check = request.form.get('check')
                checked = request.form.get('checked')
                checkers = request.form.get('checkers')
                print(check,checked,checkers)
                ##########
                getLight = requests.get("http://192.168.1.114:80/api/6A69BD6601/lights/2")
                getLight = json.loads(getLight) 
                #boolean val           
                getLight = getlight["state"]["on"]
                
                if check == 'true' and getLight == False:
                    #set device to action
                    r = requests.put(light_url, headers=light_headers, data=light_on_payload)
                    lights = True

                elif check == 'None' and getLight == True:
                    #set device to action
                    r = requests.put(light_url, headers=light_headers, data=light_off_payload)
                    lights = False

                #check return value/type for getHvac
                getHvac = requests.put(hvac_url, headers=hvac_headers, data=hvac_check_payload)
                getHvac = json.loads(getHvac)
                getHvac = getHvac["current_ma"]

                if (checked == 'true' or checkers == 'true') and getHvac == 0:
                    #set device to action
                    r = requests.put(hvac_url, headers=hvac_headers, data=hvac_on_payload) 
                    hvac = True

                elif (checked == 'None' or checkers == 'None') and getHvac == 1:
                    #set device to action
                    r = requests.put(hvac_url, headers=hvac_headers, data=hvac_off_payload)
                    hvac = False

                returnData = {'lights'  : lights,'hvac'  : hvac}
                return render_template('index.html', **returnData)   
            else:
                return render_template('index.html')
    '''

    def gen(camera):
        while genCam:
            frame = camera.get_frame()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
                
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
   
                
#called if the person is known and sends an email MUST CREATE IFTTT APPLET FOR THIS
def webpostgood():
    global last_epochs
    if (time.time() - last_epochs) > email_interval:
        last_epochs = time.time()
        print("sending email")
        requests.post('https://maker.ifttt.com/trigger/PersonDetected/with/key/c80xqPpncJSswD6G3Hc-bO', params={"value1":"Video stream","value2":"192.168.0.136:5000"})
        #DEPENDING ON WHAT U CALL IT U MUST CHANGE THIS IN IFTTT
#called if the person is unknown and sends an email
def webpostbad():
    global last_epochs
    if (time.time() - last_epochs) > email_interval:
        last_epochs = time.time()
        print("sending email")
        requests.post('https://maker.ifttt.com/trigger/UnknownPersonDetected/with/key/c80xqPpncJSswD6G3Hc-bO', params={"value1":"Video stream","value2":"192.168.0.136:5000"}) 
        #DEPENDING ON WHAT U CALL IT U MUST CHANGE THIS IN IFTTT


def facerec():
    global Positive_Ident
    global Negative_Ident
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
                positivecount += 1
                print(positivecount)
                if positivecount == 10:
                    Positive_Ident = True
                    
                    #counts the positive matches to improve accuracy and when reached activates functions    
            else:
                print("Failed")
                cv2.rectangle(framed, (x, y), (x+w, y+h), (0, 0, 255), 2)
                cv2.putText(framed, namex + str(conf), (x, y), font, 2, (0, 0 ,255), 2,cv2.LINE_AA) #will create red box and give accuracy reading
                negativecount += 1
                print(negativecount)
                if negativecount == 10:    
                     
                    Negative_Ident = True
                
        cv2.imshow('framed', framed)
        key = cv2.waitKey(1)
        rawCapture.truncate(0)
    cv2.destroyAllWindows()


#livestream()
try:
    while True:
      #  facerec()
      livestream()# this will start the stream and another recog system
except KeyboardInterrupt:    
    exit()

