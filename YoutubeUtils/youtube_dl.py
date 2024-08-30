#!/usr/bin/env python3

from pytube import Playlist, YouTube

# download directory
download_destination = '/Users/vijoy.vallachira/YouTubeDump'


# To download a single video
def download_video():
    youtube_video_source = input("Enter Youtube Video URL : ")

    # Downloading the highest resolution, progressive type video.
    print("Downloading %s" % youtube_video_source)
    YouTube(youtube_video_source).streams.get_highest_resolution().download(download_destination)

    ## YouTube(youtube_video_source).streams.filter(progressive=True, file_extension='mp4').order_by('resolution')[-1].download()
    
    return


# To download entire Playlist
def download_playlist():
    youtube_playlist = input("Enter Youtube Playlist URL : ")
    pl = Playlist(youtube_playlist)
    pl.populate_video_urls()
    print('Title of the playlist: %s' % pl.title())
    print('Number of videos in playlist: %s' % len(pl.video_urls))
    pl_video_list = pl.video_urls
    print("Downloading Playlist Videos \n")

    # printing the list using loop
    for x in range(len(pl_video_list)):
        print(str(x) + " >> " + pl_video_list[x])
        individual_video_stream = YouTube(pl_video_list[x]).streams.filter(mime_type="video/mp4").first()
        individual_video_stream.download(download_destination, "PhysicsSession"+str(x), "unAcademy-ClassXI-JEE")

    # print(*pl_video_list, sep="\n")
    # pl.download_all(download_destination)

    return


def display_video_streams():
    youtube_video_source = input("Enter Youtube URL : ")

    yt=YouTube(youtube_video_source)
    print(yt.streams)

    return


option = input("Download a Single [V]ideo OR [P]laylist OR  [Di]splay available Videos? [D, V or P] : ")
# download_destination = input("Download Directory : ")


if option == 'V':
    download_video()
elif option == 'P':
    download_playlist()
elif option == "D":
    display_video_streams()
else:
    print("Invalid Option...! Only 'D', 'V' or 'P' allowed.....")

print("Good Bye!")
