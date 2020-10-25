import socket
import pickle
import os
from datetime import datetime
from config import storageserverip

serverip = storageserverip
HEADERSIZE = 10
cachedData = []


def checkAndSend(data):
    if cachedData is not None:
        upload_cached()
    send_data(data)


def send_data(data, dCached=False):
    try:
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c.connect((serverip, 6572))
        data = pickle.dumps(data)
        data = bytes(f'{len(data):<{HEADERSIZE}}', 'utf-8') + data
        c.send(data)
    except Exception as e:
        if dCached:
            return False
        cachedData.append({'timeOfUpload': datetime.now(), 'data': data})
        print('Cached for later upload')
        print(cachedData)


def prepImage(camera, tstamp, image, store):
    if store not in os.getcwd():
        os.chdir(store)
    filename = image
    image = convertBinary(image)
    vals = (camera, tstamp, image)
    checkAndSend(vals)
    os.remove(filename)
    print('completed')


def convertBinary(image):
    with open(image, 'rb') as file:
        binaryData = file.read()
    return binaryData


def upload_cached():
    for i in range(len(cachedData)):
        if send_data(cachedData[i]['data'], dCached=True) == False:
            return
        del cachedData[i]