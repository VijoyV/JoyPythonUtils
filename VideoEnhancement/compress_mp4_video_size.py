import subprocess
from moviepy.editor import VideoFileClip

def compress_video(input_file, output_file, target_size_mb):
    # Calculate the target bitrate
    video = VideoFileClip(input_file)
    target_bitrate = (target_size_mb * 8 * 1024 * 1024) / video.duration

    # Compress the video using ffmpeg
    command = [
        "ffmpeg",
        "-i", input_file,
        "-b:v", f"{int(target_bitrate)}",
        "-bufsize", f"{int(target_bitrate * 2)}",
        output_file
    ]
    subprocess.run(command)

    # Close the video file to release resources
    video.close()

# Example usage
input_file = "C:\\WorkArea\\NCERTTextBooks\\Class-XII\\XII-English-1-Flamingo\\MP4-Videos\\Poem-01-My Mother at Sixty six.mp4"
output_file = "C:\\WorkArea\\NCERTTextBooks\\Class-XII\\XII-English-1-Flamingo\\MP4-Videos\\Poem-01-My Mother at Sixty six V1.mp4"
target_size_mb = 40
compress_video(input_file, output_file, target_size_mb)
