import nfc
import ndef
from nfc.clf import RemoteTarget
from time import sleep




class NFCController(object):

    def __init__(self):
        self._clf = nfc.ContactlessFrontend('usb')


    def block_for_target_tag(self):
        """
        Sets up a lamdba which blocks until a tag is brought near the NFC reader

        Returns:
            A Type3Tag (e.g. nfc.tag.tt2_nxp.NTAG215)
        """
        tag = self._clf.connect(rdwr={'on-connect': lambda tag: False})
        return tag

    def print_tag_data(self, tag):
        """Prints the data it finds in the NDEF record of the tag

        Args:
            tag (A Type3Tag (e.g. nfc.tag.tt2_nxp.NTAG215)): The tag for which we want to print the data
        """
        if tag.ndef is None:
            print('No data found in tag')
            return

        for record in tag.ndef.records:
            print(record)

    @staticmethod
    def get_tag_data_as_dict(tag):
        if tag.ndef is None:
            print('No data found in tag')
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

    tag = nfcController.block_for_target_tag()
    nfcController.print_tag_data(tag)


    #spotify:album:7MtJrKwP2h9eJMqnooR6iM