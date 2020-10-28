import numpy as np
import imutils
from imutils.video import VideoStream
import cv2
import datetime
import time
import threading
from camera_data_client import prep_image
import os

threadLock = threading.Lock()
streamFrame = None
print(f'at init {type(streamFrame)}')
camStream = VideoStream(src=-1).start()
time.sleep(2)
armed = False

class MotionAgent:
    def __init__(self, alpha=0.5):
        self.alpha = alpha
        self.bg = None

    def update_aw(self, image):
        if self.bg is None:
            self.bg = image.copy().astype('float')
            return
        cv2.accumulateWeighted(image, self.bg, self.alpha)

    def detect(self, image, threshVal=25):
        delta = cv2.absdiff(self.bg.astype("uint8"),
                            image)
        threshold = cv2.threshold(delta, threshVal, 255, cv2.THRESH_BINARY)[1]

        threshold = cv2.erode(threshold, None, iterations=2)
        threshold = cv2.dilate(threshold, None,
                               iterations=2)

        contours = cv2.findContours(threshold.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        (minX, minY) = (np.inf, np.inf)
        (maxX, maxY) = (-np.inf, -np.inf)

        if len(contours) == 0:
            return None

        for c in contours:
            (x, y, w, h) = cv2.boundingRect(c)
            (minX, minY) = (min(minX, x), min(minY, y))
            (maxX, maxY) = (max(maxX, x + w), max(maxY, y + h))

        return threshold, (minX, minY, maxX, maxY)


class MotionFrame:
    def __init__(self, title, image, dir):
        self.title = title
        self.image = image
        self.dir = dir

    def store(self, title, image, dir):
        if self.dir not in os.getcwd():
            os.chdir(self.dir)
        cv2.imwrite(self.title, self.image)


def motion_detection(framecount, location, store):
    global streamFrame
    global threadLock
    md = MotionAgent(alpha=0.1)
    total = 0

    while True:
        frame = camStream.read()
        frame = imutils.rotate(frame, 180)
        frame = imutils.resize(frame, width=400, height=100)
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        grey = cv2.GaussianBlur(grey, (7, 7), 0)
        timestamp = datetime.datetime.now()
        cv2.putText(frame, timestamp.strftime("%A %d %B %Y %I:%M:%S") + "" + location, (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

        if total > framecount and armed:
            motion = md.detect(image=grey)

            if motion is not None:
                start = time.time()
                (thresh, (minX, minY, maxX, maxY)) = motion
                cv2.rectangle(frame, (minX, minY), (maxX, maxY), (0, 0, 255), 2)
                filename = f"{str(timestamp.strftime('%A%d%B%Y%I:%M:%S'))}{location}.png"
                img = MotionFrame(filename, frame, store)
                img.store(img.title, img.image, img.dir)
                x = threading.Thread(prep_image(location, timestamp, filename, img.dir))
                x.start()
                end = time.time()
                print(f'execution time {end - start}')
        md.update_aw(grey)
        total += 1

        with threadLock:
            streamFrame = frame.copy()


def stream():
    global threadLock
    global streamFrame
    while True:

        with threadLock:

            if streamFrame is None:
                continue
            (flag, encodedImage) = cv2.imencode(".jpg", streamFrame)

            if not flag:
                continue

            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(
                encodedImage) + b'\r\n')
