from pytube import Playlist, YouTube


# To Download a single video
def download_video():

    youtubeVideoSource = input("Enter Youtube Video URL : ")

    yt = YouTube(youtubeVideoSource).streams.filter(subtype='mp4').first()

    print("downloading Video " + str(yt))
    yt.download(downloadDestination)

    return

# To download entire Playlist
def download_playlist() :

    youtubePlaylist = input("Enter Youtube Playlist URL : ")
    pl = Playlist(youtubePlaylist)

    # or if you want to download in a specific directory
    print("downloading Playlist " + str(pl))
    pl.download_all(downloadDestination)

    return

# download directory
downloadDestination = '/Users/vijoy.vallachira/Downloads/youtube-videos'

print("Downlaod a Single [V]ideo OR [P]laylist? [V or P] : ")
option = input()

if option=='V' :
    download_video()
elif option=='P' :
    download_playlist()
else :
    print("Invalid Option...! Only 'V' or 'P' allowed.....")

print ("Good Bye!")
