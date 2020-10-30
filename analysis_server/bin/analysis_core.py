import os
import cv2
import numpy as np

location_face_cascade = 'cascades/haarcascade_frontalface_default'

def face_detection(img):
    face_cascade = cv2.CascadeClassifier()
    face_cascade.load(location_face_cascade)

    img = cv2.imread(img)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(img)

    face = face_cascade.detectMultiScale(gray)
    for (x,y,w,h) in face:
        centre = (x + w//2, y + h//2)
        colour_image = cv2.ellipse(img, centre, (w//2, h//2), 0, 0, 360, (255, 0, 255), 4)

    cv2.imwrite(img, colour_image)

    print('completed')