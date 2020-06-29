import nfc
import ndef
from nfc.clf import RemoteTarget
from time import sleep
from enum import Enum, auto

import logging
logging.basicConfig(format='%(filename)s.%(lineno)d:%(levelname)s:%(message)s',
                    level=logging.DEBUG)



class NFCController(object):
 

    def __init__(self):
        self._clf = nfc.ContactlessFrontend('usb')

        self.currentTag = None  # Currently connected tag, if any
        self.lastTag = None     # We use this to check to see if the tag currently being read is different than the last one stored

    def is_tag_present(self):
        """Returns True if there is a tag at the reader, False else
        """
        return self.currentTag is not None

    def on_connect(self, tag):
        # If this is the first time we are reading, or there is nothing there, just set the tag
        if not self.currentTag:
            self.currentTag = tag
            logging.debug('Setting current tag: {0}'.format(NFCController.get_tag_data_as_dict(self.currentTag)))
            return

        if self.currentTag.identifier != tag.identifier:
            logging.debug('Current tag does not match new tag. Setting current tag: {0}'.format(NFCController.get_tag_data_as_dict(self.currentTag)))
            self.lastTag = self.currentTag
            self.currentTag = tag
            logging.debug(self.currentTag)

        return

    def on_release(self, tag):
        logging.debug('Calling on_release with {0}'.format(tag))
        logging.debug('Tag removed from the reader')
        self.lastTag = self.currentTag
        self.currentTag = None
        return


    def sense_for_target_tag(self):

        target = self._clf.sense(RemoteTarget('106A'))
        
        # If there's nothing there, and we think there's something there, reset
        if not target and self.currentTag:
            self.on_release(None)
            return

        # If there's something there, call on-connect
        if target:
            tag = nfc.tag.activate(self._clf, target)
            if not tag:
                logging.warning('Failed attempt to set tag from target. Likely race condition')
                return

            self.on_connect(tag)

    @staticmethod
    def print_tag_data(tag):
        """Prints the data it finds in the NDEF record of the tag

        Args:
            tag (A Type3Tag (e.g. nfc.tag.tt2_nxp.NTAG215)): The tag for which we want to print the data
        """
        if tag.ndef is None:
            logging.warning('No data found in tag')
            return

        for record in tag.ndef.records:
            print(record)

    @staticmethod
    def get_tag_data_as_dict(tag):
        if tag.ndef is None:
            logging.warning('No data found in tag')
            return None

        data_dict = {}
        for record in tag.ndef.records:
            data_dict[record.name] = record.text

        return data_dict


    def write_tag_data(self, tag, record_dict):
        """Writies data from the provided dictionary to the tag

        Preconditions: both keys and values of the dictionary are strings

        Args:
            tag (A Type3Tag (e.g. nfc.tag.tt2_nxp.NTAG215)): The tag for which we want to write the data
            record_dict (dict): The dictionary to be written to the tag (tag.ndef.records)

        throws IOError if the write fails
        """ 

        # Check to make sure that we're only trying to write strings
        if False in [ str is type(x) for x in record_dict.keys() ]:
            raise IOError('Bad type passed in for name/id of tag records')
        if False in [ str is type(x) for x in record_dict.values() ]:
            raise IOError('Bad type passed in for value of tag records')

        tags_to_write = []
        
        for k in record_dict.keys():
            tRec = ndef.TextRecord(record_dict[k])
            tRec.name = k
            tags_to_write.append(tRec)

        # TODO:  We should probably check the size of the things we're trying to write here
        #        to ensure we're not trying to write too much to the tag

        tag.ndef.records = tags_to_write
        

    def clear_tag_data(self, tag):
        tag.ndef.records = []


if __name__ == '__main__':
    nfcController = NFCController()
    # nfcController.block_for_target_tag()

    while True:
        nfcController.sense_for_target_tag()
        sleep(0.1)
        # nfcController.print_tag_data(nfcController.currentTag)

    #spotify:album:7MtJrKwP2h9eJMqnooR6iM