import socket
import pickle
import os
from config import storageserverip

##this is for sending data over sockets to the storage server

serverip = storageserverip
HEADERSIZE = 10 ##the maximum length of the message which can be sent, circa 1billion characters

def send_data(data):
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c.connect((serverip, 6572))
    data = pickle.dumps(data) ##serialise data for sending over socket
    data = bytes(f'{len(data):<{HEADERSIZE}}', 'utf-8')+data ##add headersize to data so server knows when transmission stream is completed
    c.send(data)

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
