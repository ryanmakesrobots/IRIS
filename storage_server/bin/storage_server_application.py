import socket
import pickle
from sql_connection import create_connection
import argparse
from notification_agent import sendNotification


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
                    insertImage(fulldata)
                    print('reopening connection')
                    new_data = True
                    fulldata = b''
                    clsocket, claddress = s.accept()


def insertImage(vals):
    try:
        conn, c = create_connection()
        query = f'''INSERT INTO {table} (camera, tstamp, photo) VALUES(%s, %s, %s)'''
        c.execute(query, vals)
        conn.commit()
        query = f'''SELECT MAX(photoid) FROM {table}'''
        c.execute(query, )
        id = int(c.fetchone()[0])
        sendNotification(id, table)
    except Exception as e:
        print(f'data could not be inserted: {e}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--ip', type=str, required=True,
                    help='the ip address of the storage server (for binding)')
    ap.add_argument('-t', '--table', type=str, required=True,
                    help='the table to store the camera motion data in')
    args = vars(ap.parse_args())
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((str(args['ip']), 6572))
    s.listen(15)
    table = args['table']
    server()
