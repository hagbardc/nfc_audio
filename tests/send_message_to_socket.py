import socket
import sys


host = '192.168.1.253'
port = 32413

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((host, port))
    s.sendall(sys.argv[1].encode('utf-8'))
