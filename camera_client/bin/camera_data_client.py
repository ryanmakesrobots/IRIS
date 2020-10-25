import socket
import pickle
import os
from time import datetime
from config import storageserverip

##this is for sending data over sockets to the storage server

serverip = storageserverip
HEADERSIZE = 10 ##the maximum length of the message which can be sent, circa 1billion characters
cachedData = []

def checkAndSend(data):
    if cachedData is not None:
        upload_cached()
    send_data(data)

def send_data(data, dCached=False):
    try:
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c.connect((serverip, 6572))
        data = pickle.dumps(data) ##serialise data for sending over socket
        data = bytes(f'{len(data):<{HEADERSIZE}}', 'utf-8')+data ##add headersize to data so server knows when transmission stream is completed
        c.send(data)
    except Exception as e:
        if dCached:
            return False
        cachedData.append({'timeOfUpload': datetime.now(), 'data': data})
        print('Cached for later upload')
        print(cachedData)

def prepImage(camera, tstamp, image):
    filename = image
    image = convertBinary(image)
    vals = (camera, tstamp, image)
    send_data(vals)
    os.remove(filename) ##once the image has been sent to the server storage, there's no need to keep it locally
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