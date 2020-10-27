import socket
import pickle
import os
from datetime import datetime
from config import storageserverip

serverip = storageserverip
HEADERSIZE = 10
cached_data = []


def check_and_send(data):
    if cached_data:
        upload_cached()
    send_data(data)


def send_data(data, d_cached=False):
    try:
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c.connect((serverip, 6572))
        data = pickle.dumps(data)
        data = bytes(f'{len(data):<{HEADERSIZE}}', 'utf-8') + data
        c.send(data)
    except Exception as e:
        if d_cached:
            return False
        cached_data.append({'timeOfUpload': datetime.now(), 'data': data})
        print('Cached for later upload')


def prep_image(camera, tstamp, image, store):
    if store not in os.getcwd():
        os.chdir(store)
    filename = image
    image = convert_binary(image)
    vals = (camera, tstamp, image)
    check_and_send(vals)
    os.remove(filename)
    print('completed')


def convert_binary(image):
    with open(image, 'rb') as file:
        binarydata = file.read()
    return binarydata


def upload_cached():
    for i in range(len(cached_data)):
        if not send_data(cached_data[i]['data'], d_cached=True):
            return
        del cached_data[i]
