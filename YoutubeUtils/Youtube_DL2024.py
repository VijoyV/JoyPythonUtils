#!/usr/bin/env python3

import os  # for path manipulation
import yt_dlp as youtube_dl

# download directory
download_destination = 'C:\\Users\\vijoy\\Downloads\\YouTubeVideos'


# To download a single video
def download_video():
    youtube_video_source = input("Enter Youtube Video URL : ")

    # Downloading the highest resolution progressive MP4 video
    print(f"Downloading {youtube_video_source}")
    try:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(download_destination, '%(title)s.%(ext)s'),
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_video_source])
    except Exception as e:
        print(f"Error downloading video: {e}")

    return


# To download entire Playlist
def download_playlist():
    youtube_playlist = input("Enter Youtube Playlist URL : ")

    try:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(download_destination, '%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s'),
            'noplaylist': False
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_playlist])
    except Exception as e:
        print(f"Error downloading playlist: {e}")

    return


def display_video_streams():
    youtube_video_source = input("Enter Youtube URL : ")

    try:
        ydl_opts = {
            'listformats': True
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_video_source])
    except Exception as e:
        print(f"Error displaying video streams: {e}")

    return


option = input("Download a Single [V]ideo OR [P]laylist OR [Di]splay available Videos? [D, V or P] : ")

if option == 'V':
    download_video()
elif option == 'P':
    download_playlist()
elif option == "D":
    display_video_streams()
else:
    print("Invalid Option...! Only 'D', 'V' or 'P' allowed.....")

print("Good Bye!")
