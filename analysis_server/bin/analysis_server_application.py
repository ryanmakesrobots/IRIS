import socket
import argparse
import pickle
import os
import config
from sql_connection import create_connection

HEADERSIZE = 10


def server():
    print(f'server running')
    while True:
        clsocket, claddress = s.accept()
        print(f'client connected at {claddress}')
        while True:
            fulldata = b''
            new_data = True
            while True:
                data = clsocket.recv(16)
                if new_data:
                    datalen = int(data[:HEADERSIZE])
                    new_data = False

                fulldata += data

                if len(fulldata) - HEADERSIZE == datalen:
                    print('all data recvd')
                    fulldata = pickle.loads(fulldata[HEADERSIZE:])
                    pull_images(fulldata)
                    print('reopening connection')
                    new_data = True
                    fulldata = b''
                    clsocket, claddress = s.accept()


def pull_image(vals):
    conn, c = create_connection
    id, table = vals
    query = f'''SELECT photoid, photo FROM {table} WHERE photoid is {id}'''
    c.execute(query)
    photo_bin_data = c.fetchone()[1]
    id = c.fetchone()[0]
    with open(f'{id}.png', wb) as outfile:
        outfile.write(photo_bin_data)
    return f'{id}.png'


def get_face(image):
    pass


def insert_match_data(data):
    pass


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--ip', type=str, required=True,
                    help='the ip address of the server that the application runs on')
    args = vars(ap.parse_args())
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((args['ip'], config.analysisserverport))
    s.listen(15)
    server()
