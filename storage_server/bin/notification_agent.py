import socket
from config import analysisserverip
import pickle

HEADERSIZE = 10

def send_notification(id, table):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((analysisserverip, 7821))
    data = pickles.dumps((id, table))
    data = bytes(f'{len(data):<{HEADERSIZE}}', 'utf-8')+data
    s.send(data)


