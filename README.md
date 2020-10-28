# nfc_audio

 Inspired by [a recent post on reddit](https://www.reddit.com/r/Python/comments/he081v/i_wrote_a_python_script_to_play_an_album_on_sonos/), I wanted to code something up that allowed me to manipulate physical devices to play music from my computer.  The idea here is that, given an NFC reader (which will eventually be embedded in a nice looking box) and some NFC stickers attached to printed out album art, we should be able to play music from the harddrive of a raspberry pi just by putting the album art on the box.

Instead of using the spotify apis to hook up with Sonos, we are associating spotify URIs with local paths.  Playlists are created and delivered to VLC (installed locally on the raspberry) and played through the audio jack.
 
To view a demo of the prototype:  https://youtu.be/z2we-WwWUfo

|Band|Album|Spotify URI|
|--|--|--|
|Alkaline Trio|Goddamnit!|spotify:album:3bic2qlxGauU2dVSCrinLY|
|Black Sabbath|Paranoid|spotify:album:6r7LZXAVueS5DqdrvXJJK7|
|DJ Shadow|Entroducing|spotify:album:4wvqGLk1HThPA0b5lzRK2l|
|Jobim|The Unknown Antonio Carlos Jobim|spotify:album:3ToNGp8ny9FOcjcZRn5I08|
|Lovage|Music To Make Love To Your Old Lady By|spotify:album:3QFwPfYolMmXNNdOrRLLGE|
|Muddy Waters|I'm Ready|spotify:album:4mh3XUBkBiIpCCriJ4mYNP|
|Various Artists|Moana OST|spotify:album:6pZj4nvx6lV3ulIK3BSjvs|


What the following python code does is to get a plex server object (for the desktop), get a list of albums, grabs the first album off the list, and then gets the second track from that album.  Then it gets a stream url for that track, which can be put as a path for a media_list using the vlc controller


from plexapi.myplex import MyPlexAccount  
token = 'KLs3X72-9BzWhpJSen9U'            
music = plex.library.section('Music')
baseurl = 'http://192.168.1.6:32400'
plex = PlexServer(baseurl, token)
albums = music.albums()
a = albums[0]
a.tracks()[1]
magic_number = a.tracks()[1]
for m in magic_number.media:
        print(m)
u = magic_number.getStreamURL()

from vlccontroller import *
media_list = vlc = VLCController()
print(vlc._vlcInstance)
media_list = vlc._vlcInstance.media_list_new()
media_list.add_media(vlc._vlcInstance.media_new('http://192.168.1.6:32400/audio/:/transcode/universal/start.m3u8?X-Plex-Platform=Chrome&copyts=1&mediaIndex=0&offset=0&path=%2Flibrary%2Fmetadata%2F924&X-Plex-Token=KLs3X72-9BzWhpJSen9U')
media_list.add_media(vlc._vlcInstance.media_new('http://192.168.1.6:32400/audio/:/transcode/universal/start.m3u8?X-Plex-Platform=Chrome&copyts=1&mediaIndex=0&offset=0&path=%2Flibrary%2Fmetadata%2F924&X-Plex-Token=KLs3X72-9BzWhpJSen9U'))
vlc._media_list_player.set_media_list(media_list)
vlc._media_list_player.play()