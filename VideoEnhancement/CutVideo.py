from moviepy.video.io.VideoFileClip import VideoFileClip


def cut_video(input_file, output_file, start_time, end_time):
    video = None
    try:
        # Load the video file
        video = VideoFileClip(input_file)

        # Convert start_time and end_time to seconds
        start_seconds = sum(int(x) * 60 ** i for i, x in enumerate(reversed(start_time.split(":"))))
        end_seconds = sum(int(x) * 60 ** i for i, x in enumerate(reversed(end_time.split(":"))))

        # Cut the video clip
        cut_video = video.subclip(start_seconds, end_seconds)

        # Write the result to a file
        cut_video.write_videofile(output_file, codec="libx264")
    finally:
        # Close the video file to ensure proper cleanup
        video.reader.close()
        video.audio.reader.close_proc()


if __name__ == "__main__":
    # Example usage
    input_video = "C:\\Users\\vijoy\\Downloads\\JoannaArangetramVideo\\Part-02.mp4"
    output_video = "C:\\Users\\vijoy\\Downloads\\JoannaArangetramVideo\\Dance-09.mp4"
    t1 = "01:22:01"  # Start time in HH:MM:SS
    t2 = "01:30:50"  # End time in HH:MM:SS

    cut_video(input_video, output_video, t1, t2)
