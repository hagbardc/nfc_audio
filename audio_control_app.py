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
    """App driving the physical hardware/music interface.

    Manages playing audio via VLC, driven by tags read from an NFCController

    """


    class State(Enum):
        WAITING = auto(),
        PLAYING = auto() 

    def __init__(self): 
        self._nfc = NFCController()
        self._vlc = VLCController()
        self._state = VirtualJukebox.State.WAITING

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

        logging.debug('Building medialist')
        ml = self._vlc.build_medialist_from_uri(tag_info['uri'])
        self._vlc._media_list_player.set_media_list(ml)
        self._vlc._media_list_player.play()

        logging.debug('Setting state to PLAYING')
        self._state = VirtualJukebox.State.PLAYING
        self._currentlyPlayingURI = tag_info['uri']


    def waiting_for_halt(self):
        """When called, checks to see if there is a 

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
                    self.check_tag_existence_and_play()

                if self._state == VirtualJukebox.State.PLAYING:
                    self.waiting_for_halt()

            sleep(0.1)  # There's no real need to poll the NFC device at an incredibly high frequency

        except KeyboardInterrupt:
            logging.debug('Ctrl-c interrupt:  Exiting application')
            sys.exit(0)
        





if __name__ == '__main__':
    
    app = VirtualJukebox()
    app.run()

