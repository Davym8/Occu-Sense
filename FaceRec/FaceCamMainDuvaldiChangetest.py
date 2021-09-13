"""
This is the Main file which we will be using to run both functions

first we need to import the modules and files we will be using 
"""
import cv2
import sys
from picamera.array import PiRGBArray
from picamera import PiCamera
from flask import *
from cameras import VideoCamera
from flask_basicauth import BasicAuth
import pickle
import time
import threading
import requests
username = 'admin'
pwd = 'pwd'
genCam = True
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

Positive_Ident = False
Negative_Ident = False


#Runs webserver and object/face reocgnition, using the classifiers below,
#we initialise the video camera by calling it then setup the flask server using app and credentials
def livestream():
    object_classifier = cv2.CascadeClassifier("/home/pi/Desktop/FaceRec/haarcascades/haarcascade_upperbody.xml") #opencv classifiers 
    face_classifier = cv2.CascadeClassifier("/home/pi/Desktop/FaceRec/haarcascades/haarcascade_frontalface_default.xml") # CHANGE LOCATION to where you have these 
    
    video_camera = VideoCamera() # creates a camera object
    
    
    app = Flask(__name__)
    app.config['BASIC_AUTH_USERNAME'] = 'd'
    app.config['BASIC_AUTH_PASSWORD'] = 's'
    app.config['BASIC_AUTH_FORCE'] = False
    basic_auth = BasicAuth(app)
    last_epoch = 0.0
    start = time.time()
            
#checks for objects and sends an email of the frame when object is detected
    def check_for_objects():
        last_epoch = 0.0
        update_interval = 30
        detection = 0
        try:
            while True:
                frame, found_obj = video_camera.get_object(object_classifier)
                frames, found_face = video_camera.get_object(face_classifier)
                
                if found_obj and (time.time() - last_epoch) > update_interval:
                    last_epoch = time.time()
                    
                    detection += 1
                    print(detection)
                    if detection >= 10:
                        sendEmail(frame)
                        return
        except:
            print (("Error sending email: "), sys.exc_info()[0])
    
    #this shows the route of the app and returns the index html file which will be used for creating a webpage with the video stream
    
    @app.route("/")
    @basic_auth.required
    def index():
        return render_template('index.html')
    
    @app.route("/", methods = ['POST', 'GET'])
    def shutdown_server():
        if request.method == "POST":
            usrinput = request.form['usr']
            usrpassword = request.form['pwd']
            #if usrinput != '' or usrpassword != '':
            #if 'form2' in request.form:
            if request.form['form2'] == 'SubmitShutdown':
                
                if usrinput != username:
                    return "Username or Password is incorrect!"
                if usrpassword != pwd:
                    return "Username or Password is incorrect!" 
                print("Server is shutting down")
                
                shutdown = request.environ.get('werkzeug.server.shutdown')
                if shutdown is None:
                    raise RuntimeError("Error Shutdown failed")
                else:
                    shutdown()
                    return redirect(url_for("shutdown.html", command))

            if request.form['form1'] == 'SubmitControll':
                #ToDo need to send selection back to web to display current state
                check = request.form['check']   #lights
                checked = request.form['checked']   #HVAC
                checkers = request.form['checkers']   #HVAC cool/ AIrcon
                
                getLight = #use request to get state
                getHvac  = #use request to get state


                if check == True and getLight == False:
                    # HTTP PUT data for light
                    url = "http://192.168.1.114:80/api/6A69BD6601/lights/2/state"
                    on_payload = "{\"on\":true}"
                    payload = on_payload
                    headers = {'Content-Type':'text/plain'}

                    #set device to action
                    r = requests.put(url, headers=headers, data=payload)
                    print(r)
                    lights = True

                elif check == False and getLight == True:
                    # HTTP PUT data for light
                    url = "http://192.168.1.114:80/api/6A69BD6601/lights/2/state"
                    off_payload = "{\"on\":false}"
                    payload = off_payload
                    headers = {'Content-Type':'text/plain'}

                    #set device to action
                    r = requests.put(url, headers=headers, data=payload)
                    print(r)
                    lights = False
                
                url = "https://wap.tplinkcloud.com?token=5b2a0cda-CTWBN5xjydqNigFZK0bVONb"
                payload = on_payload = json.dumps({
                        "method": "passthrough",
                        "params": {
                            "deviceId": "8006271D01FC0ED5250D5FBA3AF2B79B1E6452F1",
                            "requestData": "{\"emeter\":{\"get_realtime\":{}}}"
                        }
                        })
                headers = {'Content-Type': 'application/json'}

                getHvac = requests.put(url, headers=headers, data=payload)
                #check return value/type for getHvac

                if (checked == True or checkers == True) and getHvac == 0:
                    #HTTP PUT data for hvac
                    
                    on_payload = json.dumps({
                        "method": "passthrough",
                        "params": {
                            "deviceId": "8006271D01FC0ED5250D5FBA3AF2B79B1E6452F1",
                            "requestData": "{\"system\":{\"set_relay_state\":{\"state\":1}}}"
                    }
                    })
                    payload = on_payload
                    #set device to action
                    r = requests.put(url, headers=headers, data=payload)
                    print(r) 
                    hvac = True


                elif (checked == False or checkers == False) and getHvac == 1:

                    #HTTP PUT data for hvac
                    off_payload = json.dumps({
                        "method": "passthrough",
                        "params": {
                            "deviceId": "8006271D01FC0ED5250D5FBA3AF2B79B1E6452F1",
                            "requestData": "{\"system\":{\"set_relay_state\":{\"state\":0}}}"
                    }
                    })
                    payload = off_payload


                    #set device to action
                    r = requests.put(url, headers=headers, data=payload)
                    print(r)
                    hvac = False

                returnData = {
                    'lights'  : lights,
                    'hvac'  : hvac
                }
                return render_template('index.html', **returnData)

        else:
            return 'You need authorization to shut the server down!'
        
    
    
    def gen(camera):
        while genCam:
            frame = camera.get_frame() 
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            
            
    
    
            
    @app.route('/video_feed')
    def video_feed():
        return Response(gen(video_camera),mimetype='multipart/x-mixed-replace; boundary=frame')
    
    @app.route("/<shutdown>")
    def shutdown():
        return #f"<h1>{shutdown}</h1>"
     
    '''
    #needs chnging to form POST method
    @app.route("/<deviceName>/<action>")
    def action(deviceName, action): 
        if deviceName == 'lights':
            
            # HTTP PUT data for light
            url = "http://192.168.1.114:80/api/6A69BD6601/lights/2/state"
            on_payload = "{\"on\":true}"
            off_payload = "{\"on\":false}"
            headers = {'Content-Type':'text/plain'}
        
        if deviceName == 'hvac':
            
            #HTTP PUT data for hvac
            url = "https://wap.tplinkcloud.com?token=5b2a0cda-CTWBN5xjydqNigFZK0bVONb"
            on_payload = json.dumps({
                "method": "passthrough",
                "params": {
                    "deviceId": "8006271D01FC0ED5250D5FBA3AF2B79B1E6452F1",
                    "requestData": "{\"system\":{\"set_relay_state\":{\"state\":1}}}"
              }
            })
            off_payload = json.dumps({
                "method": "passthrough",
                "params": {
                    "deviceId": "8006271D01FC0ED5250D5FBA3AF2B79B1E6452F1",
                    "requestData": "{\"system\":{\"set_relay_state\":{\"state\":0}}}"
              }
            })
            headers = {'Content-Type': 'application/json'}

        if action == 'on':
            payload = on_payload
        if action == 'off':
            payload == off_payload

        #set device to action
        r = requests.put(url, headers=headers, data=payload)
        print(r)
        ####################################################
        '''    
      
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


livestream()
