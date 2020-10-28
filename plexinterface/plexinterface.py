from plexapi.server import PlexServer
import plexapi.exceptions

import logging

class PlexInterface(object):

    def __init__(self, servername='plexserver', port=32400, token='KLs3X72-9BzWhpJSen9U'):
        self._servername = servername
        self._port = port
        self._token = token
        
        self._plex = None
        self._music = None
        
        
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

        if artist:
            logging.warn('Narrowing search via artist name is not yet supported')

        albumList = self._music.searchAlbums(title=albumTitle)
        if not len(albumList):
            logging.warn('No albums returned with album title {0}'.format(albumTitle))
            return None

        album = albumList[0]
        return [t.getStreamURL() for t in album.tracks()]




if __name__ == '__main__':
    
    import pprint
    p = PlexInterface()
    p.connect()

    urls = p.getStreamURLsForAlbum(albumTitle='Londinium')
    pprint.pprint(urls)


