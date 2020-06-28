from nfccontroller import NFCController

import argparse
import sys
 

def parse_arguments(argv):

    parser = argparse.ArgumentParser(description='Perform some operation on an nfc tag')

    parser.add_argument('-t', dest='type',
                        choices = ['read', 'write'],
                        default='read', help='Set the operation.  \'write\' requires uri/band/album options')

    parser.add_argument('--uri', dest='uri',
                        required=False,
                        help='Data to be written to \'uri\' key of NDEF record')

    parser.add_argument('--band', dest='band',
                        required=False,
                        help='Data to be written to \'band\' key of NDEF record')

    parser.add_argument('--album', dest='album',
                        required=False,
                        help='Data to be written to \'album\' key of NDEF record')



    return parser.parse_args(argv)


def read_tag():

    nfcController = NFCController()
    tag = nfcController.block_for_target_tag()
    nfcController.print_tag_data(tag)


def write_tag(uri=None, band=None, album=None):

    if not uri or not band or not album:
        print('Write functionality requires values for uri, band, and album')
        return

    nfcController = NFCController()
    tag = nfcController.block_for_target_tag()

    data_to_write = {'uri': uri, 'band': band, 'album': album }

    print('Writing data: {0}'.format(data_to_write))
    nfcController.write_tag_data(tag, data_to_write)

    print('Reading data back...')
    newtag = nfcController.block_for_target_tag()
    nfcController.print_tag_data(newtag)






if __name__ == '__main__':
    
    args = parse_arguments(sys.argv[1:])

    try:

        if args.type == 'read':
            print('Waiting for tag...\n')
            read_tag()
            sys.exit(0)

        if args.type == 'write':
            write_tag(uri=args.uri, band=args.band, album=args.album)


    except KeyboardInterrupt:
        sys.exit(0)