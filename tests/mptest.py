from vlccontrol.vlccontroller import VLCController
import vlc


controller = VLCController()
mpl = controller._media_list_player
mp = mpl.get_media_player()
aol = mp.audio_output_device_enum()

while -1 is aol.contents.description.find(b'Polk'):
    print(aol.contents.description)
    aol = aol.contents.next

mp.audio_output_device_set(None, aol.contents.device)

uri = 'spotify:album:6kvCH4eS92QkpBNdTmjLEz' #Jimi Hendricks
media_list = controller.build_medialist_from_uri(uri)
mpl.set_media_list(media_list)
mpl.play()


while True:
    pass