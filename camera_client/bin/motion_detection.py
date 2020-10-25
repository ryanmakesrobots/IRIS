import numpy as np
import imutils
from imutils.video import VideoStream
import cv2
import datetime
import time
import threading
from camera_data_client import prepImage
import os

threadLock = threading.Lock()
streamFrame = None
print(f'at init {type(streamFrame)}')
camStream = VideoStream(src=-1).start()
time.sleep(2)


class motionAgent:
    # initialise the motionagent
    # if no value is set for the alpha [to determine the speed of decay of earlier images input]
    def __init__(self, alpha=0.5):
        self.alpha = alpha
        ##background detraction - baseline
        self.bg = None

    # update the accumulated weighted average to assess the change in image i.e. detect motion
    def updateAW(self, image):
        if self.bg is None:
            ##initiate the background with the passed image
            self.bg = image.copy().astype('float')  ##convert image to floating point number for calculation
            return
        cv2.accumulateWeighted(image, self.bg, self.alpha)

    def detect(self, image, threshVal=50):
        ##detect motion through analysis of change in image -- threshVal = threshold for difference in image, i've set mine higher to avoid light pollution as motion
        delta = cv2.absdiff(self.bg.astype("uint8"),
                            image)  ##calculate the absolute difference (delta) between the background image and the current frame
        threshold = cv2.threshold(delta, threshVal, 255, cv2.THRESH_BINARY)[
            1]  ##returns the threshold value which is used to identify changes in the frame, we take the threshold image

        threshold = cv2.erode(threshold, None, iterations=2)  ##erode the boundaries of the image, iterate over it twice
        threshold = cv2.dilate(threshold, None,
                               iterations=2)  ##dilate the image eroded image, as erosion removes whitenoise, dilation enables us to increase object area after erosion of the boundaries

        contours = cv2.findContours(threshold.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)  # get the contours from the frame -- returns a numpy array
        contours = imutils.grab_contours(contours)  ##returns tuple value
        (minX, minY) = (np.inf, np.inf)  # positive infinite floating point number in numpy
        (maxX, maxY) = (-np.inf, -np.inf)  # negative number of above

        if len(contours) == 0:
            return None  ##if the contours haven't changed then don't do anything

        for c in contours:
            (x, y, w, h) = cv2.boundingRect(c)  ##put a rectangle around the area of interest
            (minX, minY) = (min(minX, x), min(minY, y))
            (maxX, maxY) = (max(maxX, x + w), max(maxY, y + h))

        return (
        threshold, (minX, minY, maxX, maxY))  ##return the frame and the coordinates for the rectangle around the motion


class motionFrame:
    ## a class for saving a frame where motion has been detected
    def __init__(self, title, image, dir):
        self.title = title
        self.image = image
        self.dir = dir

    def store(self, title, image, dir):
        os.chdir(self.dir)
        cv2.imwrite(self.title, self.image)  ##store the frame in a given directory for processing


def motion_detection(frameCount, location, store):
    global streamFrame
    global threadLock
    md = motionAgent(alpha=0.1)
    total = 0

    while True:
        frame = camStream.read()  ##get the stream from camera
        frame = imutils.rotate(frame, 180)  ##my camera is mounted covertly and is upside down
        frame = imutils.resize(frame, width=400, height=100)
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  ##convert the image to gray
        grey = cv2.GaussianBlur(grey, (7, 7), 0)  ##blur the edges for easier line detection (less gaps)
        timestamp = datetime.datetime.now()  ##get the time!
        cv2.putText(frame, timestamp.strftime("%A %d %B %Y %I:%M:%S") + "" + location, (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255),
                    1)  ##add the timestamp and the location to the original frame for feeding back

        if total > frameCount:  ##this ensures we have captured a second of the video footage as we define the fps in the argument for this function
            motion = md.detect(image=grey)  ##use the detection function in the class

            if motion is not None:
                start = time.time()  ## for perfomance monitoring purposes, i see how long it takes to complete the distributed analysis vs the single node
                (thresh, (minX, minY, maxX,
                          maxY)) = motion  ##the return from our function is the image and the coordinates of the rectangle we're going to place
                cv2.rectangle(frame, (minX, minY), (maxX, maxY), (0, 0, 255),
                              2)  ## draw the rectangle on the frame, it's red and it has the thickness of 2
                filename = f"{str(timestamp.strftime('%A%d%B%Y%I:%M:%S'))}{location}.png"  ## set the filename with the timestamp and location
                img = motionFrame(filename, frame,
                                  store)  ###create an object of the frame where motion has been detected
                img.store(img.title, img.image, img.dir)  ##use the storage function of the object
                x = threading.Thread(prepImage(location, timestamp,
                                               f'{store}/{filename}'))  ##use the client communication module to send data to the storage server - create a multithread to do this
                x.start()  ##start the thread
                end = time.time()  ##the end of the processing time - for calculating the total time for processing
                print(f'execution time {end - start}')
        md.updateAW(grey)  ##update the frame with the grey image for the accumulated weight
        total += 1  ##iterate the total frames by 1

        with threadLock:  ##
            streamFrame = frame.copy()


def stream():
    global threadLock
    global streamFrame
    while True:

        with threadLock:

            if streamFrame is None:
                continue
            (flag, encodedImage) = cv2.imencode(".jpg", streamFrame)  ##encode the image for joining into the stream

            if not flag:
                continue

            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(
                encodedImage) + b'\r\n')  ##a string of images which act as a video stream
