from pytube import YouTube

# To download a video directly
YouTube('https://youtu.be/aW2m-BtCJyE?list=PLXnuiPYlDoSYiZ3ykM04N_5GwgkL4_E-9').streams.get_highest_resolution().download()
# yt = YouTube('http://youtube.com/watch?v=9bZkp7q19f0')
# yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution')[-1].download()

# To download from Playlist
from pytube import Playlist
playlist = Playlist("https://www.youtube.com/playlist?list=PLynhp4cZEpTbRs_PYISQ8v_uwO0_mDg_X")
for video in playlist:
    video.streams.get_highest_resolution().download()