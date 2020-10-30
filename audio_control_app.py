#!/usr/bin/python3.7 

from nearfield.nfccontroller import NFCController
from vlccontrol.vlccontroller import VLCController
#from socketmonitor.socketmonitor import music_socket_monitor_worker


from multiprocessing import Process, Queue
from enum import Enum, auto
import logging
import sys
from time import sleep
import json

logging.basicConfig(format='%(filename)s.%(lineno)d:%(levelname)s:%(message)s',
                    level=logging.DEBUG)

class VirtualJukebox(object):
    """App driving the physical hardware/music interface.

    Manages playing audio via VLC, driven by tags read from an NFCController

    """


    class State(Enum):
        WAITING = auto(),
        PLAYING = auto() 

    class PlayType(Enum):
        NONE = auto(),  # Not playing anything.  Should be the case when self._state = WAITING
        NFC = auto(),   # Playing audio from the NFC reader
        STREAM = auto() # Playing audio from a streaming source (e.g. Plex)

    def __init__(self, nfcQueue, socketQueue): 
        self._nfc = NFCController(message_queue = nfcQueue)
        self._vlc = VLCController()
        self._state = VirtualJukebox.State.WAITING
        self._playType = VirtualJukebox.PlayType.NONE
        self._currentlyPlayingURI = None

        self._nfcQueue = nfcQueue
        self._socketQueue = socketQueue


    def process_queue_message(self, message):
        """Takes in a message from the data sources, and triggers audio events as appropriate

        Args:
            message (str): JSON string describing an event from the source, and necessary audio data
        """
        
        # Convert the string to a dict, and validate the content
        try:
            messageDict = json.loads(message)
        except json.decoder.JSONDecodeError as err:
            logging.error('Invalid JSON string on queue: [{0}]'.format(message))
            return
        
        if messageDict['source'] == 'nfc':
            self._process_queue_message__nfc(messageDict)
        elif messageDict['source'] == 'plex':
            self._process_queue_message__plex(messageDict)
        else:
            logging.error('Invalid source: [{0}]'.format(message))


    def _process_queue_message__nfc(self, messageDict):

        tag_info = messageDict['data']

        if messageDict['event'] == 'start':
            
            if tag_info['uri'] == self._currentlyPlayingURI:
                self._vlc._media_list_player.play()
                self._state = VirtualJukebox.State.PLAYING
                self._playType = VirtualJukebox.PlayType.NFC
                return

            self._vlc._media_list_player.stop()
            logging.debug('Building medialist')
            ml = self._vlc.build_medialist_from_uri(tag_info['uri'])
            self._vlc._media_list_player.set_media_list(ml)
            self._vlc._media_list_player.play()

            logging.debug('Setting state to PLAYING')
            self._state = VirtualJukebox.State.PLAYING
            self._playType = VirtualJukebox.PlayType.NFC
            self._currentlyPlayingURI = tag_info['uri']

        # We only request a stop command if we're playing audio triggered by the NFC device
        if messageDict['event'] == 'stop' and self._playType == VirtualJukebox.PlayType.NFC:
            logging.debug('Tag is no longer present.  Stopping music')
            logging.debug('Setting state to WAITING')
            self._vlc._media_list_player.pause()
            self._state = VirtualJukebox.State.WAITING
            self._playType = VirtualJukebox.PlayType.NONE



    def run(self):

        try:
            while True:

                # This pings the NFC, updates its internal tag states, and will push a message onto 
                # the NFCQueue
                self._nfc.sense_for_target_tag()

                # Poll the queues to see if there's anything in there waiting for me
                for q in [self._nfcQueue, self._socketQueue]:
                    if q and not q.empty():
                        message = q.get(block=False, timeout=0.01)
                        if not message:
                            continue

                        logging.debug('Message from queue: {0}'.format(message) )
                        self.process_queue_message(message)


            sleep(0.1)  # There's no real need to poll the NFC device at an incredibly high frequency

        except KeyboardInterrupt:
            logging.debug('Ctrl-c interrupt:  Exiting application')
            sys.exit(0)
        





if __name__ == '__main__':
    
    host = 'nfcaudioserver'
    port = 32413

    nfcQueue = Queue()
    #socketQueue = Queue()

    #socket_process = Process(target = music_socket_monitor_worker, args=(host, port, socketQueue,))
    #socket_process.start()

    try:
        app = VirtualJukebox(nfcQueue, None)
        app.run()
    except (KeyboardInterrupt, SystemExit):
        pass

    #logging.debug('Joining the socket process')
    #socket_process.join()
