from pytube import Playlist, YouTube

# Download Path
download_path = "C:\\Users\\vijoy\\Downloads\\YouTubeVideos"

# URL of the YouTube playlist or Video
url = "https://www.youtube.com/watch?v=HaAi2cTAYVE"

def download_captions(yt, output_path):
    # Download closed captions
    captions = yt.captions
    caption = captions.get_by_language_code('en')
    if caption:
        print(f"Downloading captions for {yt.title}...")
        caption.download(title=f"{yt.title}_captions", output_path=output_path)
    else:
        print(f"No captions available for {yt.title}")

def download_video(url, output_path):
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(file_extension='mp4').get_highest_resolution()
        if stream:
            print(f"Downloading {yt.title}...")
            stream.download(output_path=output_path)
            download_captions(yt, output_path)
        else:
            print(f"No MP4 format available for {yt.title}")
    except Exception as e:
        print(f"An error occurred: {e}")

def download_playlist(playlist_url, output_path):
    try:
        playlist = Playlist(playlist_url)
        print(f"Found {len(playlist.video_urls)} videos in the playlist.")
        for video in playlist.video_urls:
            download_video(video, output_path)
    except Exception as e:
        print(f"An error occurred while processing the playlist: {e}")

if __name__ == "__main__":
    if "playlist" in url:
        print('Downloading Playlist...')
        download_playlist(url, download_path)
    else:
        print('Downloading just a Video...')
        download_video(url, download_path)
