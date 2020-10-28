from motion_detection import stream, motion_detection, streamFrame, set_cam_state
from imutils.video import VideoStream
from flask import Flask, Response, render_template, jsonify
import threading
import argparse
import time


localStore = 'store'

app = Flask(__name__)


@app.route('/video_stream')
def video_stream():
    print('video streaming has started')
    return Response(stream(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route('/api/v1/command/<var>')
def api_command(var):
    var = var.upper()
    if var == 'ARM':
        set_cam_state(True)
        return jsonify(f'Device {args["location"]} is now armed')
    elif var == 'DISARM':
        set_cam_state(False)
        return jsonify(f'Device {args["location"]} is unarmed')
    else:
        return jsonify('Unknown')


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
    t = threading.Thread(target=motion_detection, args=(args['frames'], args['location'], localStore,))
    t.daemon = True
    t.start()

    app.run(host=args['ip'], port=args['port'], debug=True, threaded=True, use_reloader=False)
