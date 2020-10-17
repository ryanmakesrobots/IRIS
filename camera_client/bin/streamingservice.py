from motion_detection import stream, motion_detection, streamFrame
from imutils.video import VideoStream
from flask import Flask, Response, render_template, jsonify
import threading
import argparse
import time

localStore = './store' ##the location of the local store where images are temporarily stored
#streamFrame = None ##frame for streaming
#threadLock = threading.Lock() ##define a lock for multithreading locking

##define the flask application which will start the stream

app = Flask(__name__)

#camStream = VideoStream(src=-1).start() ## for raspi cam on the pi zero this is the best method for accessing the camera from the camera port
#time.sleep(2) ## allow the camera time to warmup

##because this is a small application, all of the Flask programming is done in this one file
@app.route('/video_stream')
def video_stream():
    print('video streaming has started')
    return(Response(stream(), mimetype="multipart/x-mixed-replace; boundary=frame"))

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--ip', type=str, required=True,
                    help='ip address of the client camera')
    ap.add_argument('-x', '--port', type=int, required=True,
                    help='what port should the camera web server run on')
    ap.add_argument('-s', '--storageserver', type=str, required=True,
                    help='the ip address of the storage processing server')
    ap.add_argument('-l', '--location', type=str, required=True,
                    help='the location of the camera, for storage purposes')
    ap.add_argument('-f', '--frames', type=int, required=True,
                    help='the number of frames to form the bg model on (10+ is good)')
    args = vars(ap.parse_args())
    storageServer = args['storageserver']
    t = threading.Thread(target=motion_detection, args=(args['frames'],args['location'],localStore,))
    t.daemon = True
    t.start()

    app.run(host=args['ip'], port=args['port'], debug=True, threaded=True, use_reloader=False)
