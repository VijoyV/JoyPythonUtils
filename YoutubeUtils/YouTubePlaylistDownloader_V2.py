import yt_dlp


def download_video_best_combined(video_url, output_path):
    ydl_opts = {
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'format': 'best[ext=mp4]/best',  # Download the best combined stream with video + audio
        'postprocessors': [],  # Disable any post-processing
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])


def download_playlist_best_combined(playlist_url, output_path):
    ydl_opts = {
        'outtmpl': f'{output_path}/%(playlist_title)s/%(title)s.%(ext)s',
        'format': 'best[ext=mp4]/best',  # Download the best combined stream with video + audio
        'postprocessors': [],  # Disable any post-processing
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([playlist_url])


# Example usage
download_path = "C:\\Users\\vijoy\\Downloads\\YouTubeVideos"
playlist_url = "https://www.youtube.com/watch?v=xwYRCsX4zcc"
download_playlist_best_combined(playlist_url, download_path)



