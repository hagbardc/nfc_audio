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
