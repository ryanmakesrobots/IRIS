import socket
import pickle
from sql_connection import create_connection
import argparse
from notification_agent import send_notification


HEADERSIZE = 10


def server():
    print(f'server running')
    while True:
        clsocket, claddress = s.accept()
        print(f'client connected at {claddress}')
        while True:
            full_data = b''
            new_data = True
            while True:
                data = clsocket.recv(16)
                if new_data:
                    data_len = int(data[:HEADERSIZE])
                    new_data = False

                full_data += data

                if len(full_data) - HEADERSIZE == data_len:
                    print('all data recvd')
                    full_data = pickle.loads(full_data[HEADERSIZE:])
                    insert_image(full_data)
                    print('reopening connection')
                    new_data = True
                    full_data = b''
                    clsocket, claddress = s.accept()


def insert_image(vals):
    try:
        conn, c = create_connection()
        query = f'''INSERT INTO {table} (camera, tstamp, photo) VALUES(%s, %s, %s)'''
        c.execute(query, vals)
        conn.commit()
        query = f'''SELECT MAX(photoid) FROM {table}'''
        c.execute(query, )
        id = int(c.fetchone()[0])
        send_notification(id, table)
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
