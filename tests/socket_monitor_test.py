import logging
import socket
import sys


host = '192.168.1.253'
port = 32413


'''
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((host, port))
    s.sendall(sys.argv[1].encode('utf-8'))
'''


from multiprocessing import Process, Queue
import sys

from socketmonitor.socketmonitor import music_socket_monitor_worker



if __name__ == '__main__':
    logging.basicConfig(format='%(filename)s.%(lineno)d:%(levelname)s:%(message)s',
                            level=logging.DEBUG)
    logging.debug('Starting')

    q = Queue()

    socket_process = Process(target = music_socket_monitor_worker, args=(host, port, q,))
    socket_process.start()

    while True:
        if not q.empty():
            message = q.get(block=False, timeout=0.1)
            if not message:
                continue
            logging.debug('Message is [{0}]'.format(message))



