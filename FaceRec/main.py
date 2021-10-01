import cv2
import sys
from flask import Flask, render_template, Response
from camera import VideoCamera
from flask_basicauth import BasicAuth
import time
import threading
"""
this will run the video stream this main file is on its own and will incorporate the mail and camera 
files to run this is a standalone file and will run on its own if you want to
 
"""


def livestream():
    
    video_camera = VideoCamera() # creates a camera object, flip vertically
    object_classifier = cv2.CascadeClassifier("/home/pi/opencv/data/haarcascades/haarcascade_upperbody.xml",) # an opencv classifier
    face_classifier = cv2.CascadeClassifier("/home/pi/opencv/data/haarcascades/haarcascade_frontalface_default.xml") #must change for your filesystem
    # App Globals (do not edit) 
    app = Flask(__name__)
    app.config['BASIC_AUTH_USERNAME'] = 'd'
    app.config['BASIC_AUTH_PASSWORD'] = 's'
    app.config['BASIC_AUTH_FORCE'] = True
    last_epoch = 0.0
    basic_auth = BasicAuth(app)
    
    def check_for_objects():
        last_epoch = 0.0
        try:
            while True:
                frame, found_obj = video_camera.get_object(object_classifier)
                frames, found_face = video_camera.get_object(face_classifier)
        except:
            print (("Error for check objects: "), sys.exc_info()[0])
    
    
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
    
    
    if __name__ == '__main__':
        t = threading.Thread(target=check_for_objects, args=())
        t.daemon = True
        t.start()
        app.run(host='0.0.0.0', debug=False, threaded=False)
try:
    while True: 
        livestream()        
except KeyboardInterrupt:    
    exit()
