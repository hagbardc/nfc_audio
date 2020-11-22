from plexapi.server import PlexServer
import plexapi.exceptions

# Used to calculate similarity metrics for artist names
from difflib import SequenceMatcher

import logging
logging.basicConfig(format='%(filename)s.%(lineno)d:%(levelname)s:%(message)s',
                    level=logging.DEBUG)

class PlexInterface(object):

    def __init__(self, servername='plexserver', port=32400, token='KLs3X72-9BzWhpJSen9U', logger=None):
        self._servername = servername
        self._port = port
        self._token = token
        
        self._plex = None
        self._music = None
        self._logger = logger

        if not logger:
            self._logger = logging.getLogger('PlexInterface')
            self._logger.setLevel(logging.DEBUG)
        
        
    def connect(self):

        baseurl = 'http://{0}:{1}'.format(self._servername, self._port)

        try:
            self._plex = PlexServer(baseurl, self._token)
        except plexapi.exceptions.Unauthorized as e:
            logging.error('Authorization error when connecting to plex')
            raise e

        self._music = self._plex.library.section("Music")

    def getStreamURLsForAlbum(self, albumTitle, artist=None):
        """Finds the album of the specified name from the Plex server, returns a list of stream urls for the tracks

        If multiple albums are found, will attempt to identify the correct one using the artist name, if passed in
        If no artist name is passed in, will play the first album returned from Plex

        Args:
            album (str): Name of the album
            artist (str, optional): Name of the artist. Defaults to None.

        Returns: A list of stream urls (str), or None if no album was found/error
        """

        albumList = self._music.searchAlbums(title=albumTitle)
        if not len(albumList):
            self._logger.warn('No albums returned with album title {0}'.format(albumTitle))
            return None

        # If only one album was returned, or a artist name hint was not passed in
        # just play the first album returned
        if len(albumList) == 1 or not artist:
            album = albumList[0]
            self._logger.debug('Returning artist / album {0} / {1}'.format(album.artist().title, albumTitle))
            return [t.getStreamURL() for t in album.tracks()]

        # If more than one album was returned, use the artist hint passed in to help decide on an album
        albumNameDiffs = []
        for album in albumList:
            ratio = SequenceMatcher(None, album.artist().title, artist).ratio()
            albumNameDiffs.append(ratio)
            print('Similarity between {0} and {1} is {2}'.format(album.artist().title, artist, ratio))

        indexOfalbumToPlay = albumNameDiffs.index(max(albumNameDiffs))
        album = albumList[indexOfalbumToPlay]
        self._logger.debug('Returning artist / album {0} / {1}'.format(album.artist().title, albumTitle))


        return [t.getStreamURL() for t in album.tracks()]

        



if __name__ == '__main__':
    
    import pprint
    p = PlexInterface()
    p.connect()

    urls = p.getStreamURLsForAlbum(albumTitle='Light')
    pprint.pprint(urls)

    urls = p.getStreamURLsForAlbum(albumTitle='Light', artist='KMFDM')
    pprint.pprint(urls)

