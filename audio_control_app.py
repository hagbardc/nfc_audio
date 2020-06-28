#!/usr/bin/python3.7 

from nearfield.nfccontroller import NFCController
from vlccontrol.vlccontroller import VLCController

import sys

if __name__ == '__main__':
    
    nfc = NFCController()

    v = VLCController()

    tag = nfc.block_for_target_tag()

    print('Found tag: {0}'.format(tag))
    tag_info = NFCController.get_tag_data_as_dict(tag)

    print('tag_info: {0}'.format(tag_info))
    ml = v.build_medialist_from_uri(tag_info['uri'])
    v._media_list_player.set_media_list(ml)
    v._media_list_player.play()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        sys.exit(0)
