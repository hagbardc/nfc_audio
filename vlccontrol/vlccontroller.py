import vlc
 
from os import listdir
from os.path import isfile, isdir, join

import logging

class VLCController(object):  

    # We're using spotify uris here even though we aren't actually playing the music via spotify
    # This is primarily because I want to be be able to play the music via spotify without re-encoding
    # all of the NFC stickers
    localAudioRegistry = {
        '0JAGz65j3Yn5O789bhDSwh': '/home/pi/Documents/audio/Jobim/The Man From Ipanema/',
        'dr_octagon_instrumentalyst': '/home/pi/Documents/audio/Dr Octagon/Instrumentalyst (Octagon Beats)/',
        '10E4WkTiRDqNnL0qdlXB5b': '/home/pi/Documents/audio/The Smiths/Singles/',
        '695W2j99IV98nTIbpJScPu': '/home/pi/Documents/audio/Fitz And The Tantrums/Pickin\' Up The Pieces/',
        '4mh3XUBkBiIpCCriJ4mYNP': '/home/pi/Documents/audio/Muddy Waters/I\'m Ready/',
        'daft_punk_get_lucky':    '/home/pi/Documents/audio/Daft Punk/Get Lucky/',
        '3ToNGp8ny9FOcjcZRn5I08': '/home/pi/Documents/audio/Jobim/The Unknown Antonio Carlos Jobim/',
        '3bic2qlxGauU2dVSCrinLY': '/home/pi/Documents/audio/Alkaline Trio/Goddamnit!',
        '6pZj4nvx6lV3ulIK3BSjvs': '/home/pi/Documents/audio/Soundtrack/Moana/',
        '3QFwPfYolMmXNNdOrRLLGE': '/home/pi/Documents/audio/Lovage/Music To Make Love To Your Old Lady By/',
        '4wvqGLk1HThPA0b5lzRK2l': '/home/pi/Documents/audio/DJ Shadow/Endtroducing/',
        'desmond_dekker_rockin':  '/home/pi/Documents/audio/Desmond Dekker/Rockin\' Steady The Best of Desmond Dekker/',
        '6r7LZXAVueS5DqdrvXJJK7': '/home/pi/Documents/audio/Black Sabbath/Paranoid/'
    }

    def __init__(self):
        
        self._vlcInstance = vlc.Instance()
        self._media_list_player = self._vlcInstance.media_list_player_new()

        

    @staticmethod
    def is_path_to_audio_file(path):
        if not isfile(path):
            return False
        
        if not path.endswith('mp3') and not path.endswith('wav'):
            return False

        return True

    def stop(self):
        """Sends a stop the the currently playing media (if any)
        """
        self._media_list_player.stop()


    def get_audio_filepaths_from_path(self, path):
        """Given a path, will return a playlist suitable for delivery to the vlc.MediaPlayer

        Args:
            path (str): Either a path to a directory of files, or full path to file

        Returns:
            list of strings, paths to the audio files in the given directory (or the file specified)
        """

        filelist = []

        if VLCController.is_path_to_audio_file(path):
            return filelist.append(path)

        if not isdir(path):
            return filelist

        for f in listdir(path):
            
            full_file_path = join(path, f)
            if not VLCController.is_path_to_audio_file(full_file_path): 
                continue
            
            filelist.append(full_file_path)

        return filelist


    def convert_filepaths_to_medialist(self, filepaths):
        """This takes in a list of file paths (to audio files) and converts it to a media list

        Args:
            filepaths (list): List of strings, paths to audio files

        Returns:
            vlc.media_list object
        """
        media_list = self._vlcInstance.media_list_new()

        for f in filepaths:
            media_list.add_media(self._vlcInstance.media_new(f))

        return media_list


    def build_medialist_from_uri(self, uri):
        """Given a uri of a type supported by this controller, construct and return a medialist

        As of right now, we support spotify-style uris (e.g. spotify:album:<id>).  The only 
        portion which is relevant is the <id>, which is looked up in a local table
        Args:
            uri (str): A uri of the type supported by this controller.  (e.g. spotify:album:<id>)

        Returns:
            vlc.media_list object
        """

        split_uri = uri.split(':')
        media_list = None
        
        if split_uri[0] == 'local' or split_uri[0] == 'spotify':
            
            uri_key = split_uri[len(split_uri)-1]
            album_location = VLCController.localAudioRegistry[uri_key]
            filepaths =  sorted(self.get_audio_filepaths_from_path(album_location))
            media_list = self.convert_filepaths_to_medialist(filepaths)


        if not media_list:
            logging.error('No valid media list was created. Probable URI error on tag')
        return media_list




if __name__ == '__main__':

    import sys

    uri = 'spotify:album:7MtJrKwP2h9eJMqnooR6iM'  # Alkaline Trio

    v = VLCController()
    if len(sys.argv) > 1:
        uri = sys.argv[1]

    ml = v.build_medialist_from_uri(uri)
    v._media_list_player.set_media_list(ml)
    v._media_list_player.play()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        sys.exit(0)



