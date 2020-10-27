import socket
import pickle
import os
from threading import Thread
from datetime import datetime
from config import storageserverip

serverip = storageserverip
HEADERSIZE = 10
cached_data = []
cache_upload_in_progress = False


def check_and_send(data):
    try:
        send_data(data)
        uc_thread = Thread(target=upload_cached())
        uc_thread.start()
    except Exception as e:
        print(e)
        print('will cache data')
        cached_data.append({'timeOfUpload': datetime.now(), 'data': data})


def send_data(data):
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c.connect((serverip, 6572))
    data = pickle.dumps(data)
    data = bytes(f'{len(data):<{HEADERSIZE}}', 'utf-8') + data
    c.send(data)


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
    x = 0
    if cached_data:
        while x < len(cached_data):
            print('loading into cached data')
            for i, data in enumerate(cached_data):
                print(f'index of {i}')
                try:
                    x += 1
                    print(data['data'])
                    send_data(data['data'])
                    del (cached_data[i])
                except Exception as e:
                    print('failed to upload cached data', e)
                    return
    else:
        return