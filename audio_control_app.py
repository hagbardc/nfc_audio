#!/usr/bin/python3.7 

from nearfield.nfccontroller import NFCController
from vlccontrol.vlccontroller import VLCController

from enum import Enum, auto
import logging
import sys
from time import sleep

logging.basicConfig(format='%(filename)s.%(lineno)d:%(levelname)s:%(message)s',
                    level=logging.DEBUG)

class VirtualJukebox(object):

    class State(Enum):
        WAITING = auto(),
        PLAYING = auto()

    def __init__(self):
        self._nfc = NFCController()
        self._vlc = VLCController()
        self._state = VirtualJukebox.State.WAITING
        self._currentlyPlayingURI = None  # We'll use this to check against when looking for changes in NFC state


    def waiting_for_tag(self):
        """When called, this is going to block and continually poll the NFC Reader until a tag is put near it
        """
        
        # This is a blocking call.  Will set 'tag' to the tag presented to the reader
        if not self._nfc.currentTag:
            return

        
        tag_info = NFCController.get_tag_data_as_dict(self._nfc.currentTag)
        logging.debug('Tag info: {0}'.format(tag_info))

        logging.debug('Building medialist')
        ml = self._vlc.build_medialist_from_uri(tag_info['uri'])
        self._vlc._media_list_player.set_media_list(ml)
        self._vlc._media_list_player.play()

        logging.debug('Setting state to PLAYING')
        self._state = VirtualJukebox.State.PLAYING
        self._currentlyPlayingURI = tag_info['uri']


    def waiting_for_halt(self):
        """Blocking call which will stop the music if the current tag is removed (or replaced)

        Will make appropriate state changes as necessary
        """
        if self._nfc.is_tag_present():
            return

        logging.debug('Tag is no longer present.  Stopping music')
        logging.debug('Setting state to WAITING')
        self._vlc._media_list_player.stop()
        self._state = VirtualJukebox.State.WAITING
        return
        

    def run(self):

        try:
            while True:
                self._nfc.sense_for_target_tag()
                if self._state == VirtualJukebox.State.WAITING:
                    self.waiting_for_tag()

                if self._state == VirtualJukebox.State.PLAYING:
                    self.waiting_for_halt()

            sleep(0.1)

        except KeyboardInterrupt:
            logging.debug('Ctrl-c interrupt:  Exiting application')
            sys.exit(0)
        





if __name__ == '__main__':
    
    app = VirtualJukebox()
    app.run()

