#!/usr/bin/python3.7 

from nearfield.nfccontroller import NFCController
from vlccontrol.vlccontroller import VLCController
from socketmonitor.socketmonitor import music_socket_monitor_worker


from multiprocessing import Process, Queue
from enum import Enum, auto
import logging
import sys
from time import sleep

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
        self._nfc = NFCController()
        self._vlc = VLCController()
        self._state = VirtualJukebox.State.WAITING
        self._playType = VirtualJukebox.PlayType.NONE
        self._currentlyPlayingURI = None

        self._nfcQueue = nfcQueue
        self._socketQueue = socketQueue


    def check_tag_existence_and_play(self):
        """ When called, will check to ensure a tag is present and plays the music associated with the tag

        This is only called when transferring from a WAITING state, and transitions to a PLAYING state
        """
        
        if not self._nfc.currentTag:
            return

        if not self._state == VirtualJukebox.State.WAITING:
            logging.error('check_tag_existence_and_play called from inappropriate state.  Returning as no-op')
            return 

        
        tag_info = NFCController.get_tag_data_as_dict(self._nfc.currentTag)
        logging.debug('Tag info: {0}'.format(tag_info))

        if not tag_info:
            logging.error('Attempt to get tag info failed: Race condition?')
            return

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


    def waiting_for_halt(self):
        """When called, checks to see if there is a 

        Will make appropriate state changes as necessary
        """

        if self._nfc.is_tag_present():
            return

        logging.debug('Tag is no longer present.  Stopping music')
        logging.debug('Setting state to WAITING')
        self._vlc._media_list_player.pause()
        self._state = VirtualJukebox.State.WAITING
        self._playType = VirtualJukebox.PlayType.NONE
        return
        

    def run(self):

        try:
            while True:
                self._nfc.sense_for_target_tag()
                if self._state == VirtualJukebox.State.WAITING:
                    self.check_tag_existence_and_play()

                if self._state == VirtualJukebox.State.PLAYING:
                    self.waiting_for_halt()
                

                # Poll the queues to see if there's anything in there waiting for me
                for q in [self._nfcQueue, self._socketQueue]:
                    if not q.empty():
                        message = q.get(block=False, timeout=0.01)
                        if not message:
                            continue

                        logging.debug('Message from queue: {0}'.format(message) )


            sleep(0.1)  # There's no real need to poll the NFC device at an incredibly high frequency

        except KeyboardInterrupt:
            logging.debug('Ctrl-c interrupt:  Exiting application')
            sys.exit(0)
        





if __name__ == '__main__':
    
    host = 'nfcaudioserver'
    port = 32413

    nfcQueue = Queue()
    socketQueue = Queue()

    socket_process = Process(target = music_socket_monitor_worker, args=(host, port, socketQueue,))
    socket_process.start()

    app = VirtualJukebox(nfcQueue, socketQueue)
    app.run()

