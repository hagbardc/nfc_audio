import socket
import logging

import queue
import time

def music_socket_monitor_worker( host, port, message_queue, logging = logging.getLogger()):
    """Generates a SocketMonitor object, and sets it to listening to the port

    The SocketMonitor will listen to data coming in on the specified socket, and if it
    receives a JSON message, will pass it into the message queue

    Args:
        host (str): Socket loopback interface.  Since we want to accept requests from anything on the network, should be an empty string
        port (int): Port on which we're listening to the open socket
        message_queue (queue.Queue): Queue onto which we'll publish any valid JSON that comes in
        logging (logging.Logger, optional): Logger for publishing. Defaults to logging.getLogger().
    """
    socket_monitor = MusicSocketMonitor(host, port, audio_message_queue = message_queue)
    socket_monitor.startSocketListening()






class MusicSocketMonitor(object):

    def __init__(self, host = '', port = 32413, audio_message_queue = None, logger = logging.getLogger()):
        self._host = host
        self._port = port
        self._logger = logger
        self._messageQueue = audio_message_queue

    
    def startSocketListening(self):

        while True:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((self._host, self._port))
            s.listen()
            conn, addr = s.accept()
            with conn:
                data = None
                self._logger.debug('Connected by {0}'.format(addr))
                while True:
                    data = conn.recv(1024)  # This means the max album/artist payload size will be 1024 bytes
                    if not data:
                        break
                    self._logger.debug('Data: [{0}]'.format(data))
                    self._sendMessageOnQueue(data)

            self._logger.debug('Calling close')
            s.close()
            time.sleep(0.1)  # We put a little sleep in here to give the process time to open and close the socket

    
    def _sendMessageOnQueue(self, message):
        self._logger.debug("Putting message on queue: {0}".format(message))
        self._messageQueue.put(message)


        
if __name__ == '__main__':

    logging.basicConfig(format='%(filename)s.%(lineno)d:%(levelname)s:%(message)s',
                            level=logging.DEBUG)
    logging.debug('Starting')


    msm = MusicSocketMonitor()
    msm.startSocketListening()