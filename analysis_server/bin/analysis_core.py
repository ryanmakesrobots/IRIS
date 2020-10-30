import os
import cv2
import numpy as np

location_face_cascade = 'cascades/haarcascade_frontalface_default.xml'

def face_detection(img):
    fname = img
    if 'imagestore/unclassified' in os.getcwd():
        os.chdir('..')
        os.chdir('..')

    face_cascade = cv2.CascadeClassifier()
    face_cascade.load(location_face_cascade)

    if 'imagestore/unclassified' not in os.getcwd():
        os.chdir('imagestore/unclassified')

    img = cv2.imread(img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    face = face_cascade.detectMultiScale(gray)

    if len(face) == 0:
        print('no face detected')
        os.remove(fname)
    else:
        for (x,y,w,h) in face:
            centre = (x + w//2, y + h//2)
            colour_image = cv2.ellipse(img, centre, (w//2, h//2), 0, 0, 360, (255, 0, 255), 4)
            os.chdir('face')
            cv2.imwrite(fname, colour_image)
