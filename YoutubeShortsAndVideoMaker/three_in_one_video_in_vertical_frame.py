from moviepy.editor import VideoFileClip, CompositeVideoClip


def create_vertical_video_with_audio(video_paths, output_file="vertical_output_with_audio.mp4"):
    """
    Create a video with three input videos displayed vertically (top, middle, bottom)
    in a YouTube Shorts-style vertical format, using the audio from the middle video.
    Args:
        video_paths (list): Paths to three video files.
        output_file (str): Path for the output video file.
    """
    if len(video_paths) != 3:
        print("Error: Exactly 3 video paths are required.")
        return

    try:
        # Load the three video files
        print("Loading video files...")
        clips = [VideoFileClip(path) for path in video_paths]

        # Resize each clip to 1/3 of the frame height
        frame_width = 1080  # Standard YouTube Shorts width
        frame_height = 1920  # Standard YouTube Shorts height
        subframe_height = frame_height // 3  # Each video occupies 1/3 of the height

        print("Resizing video clips...")
        resized_clips = [clip.resize(width=frame_width) for clip in clips]

        # Position each clip vertically
        print("Positioning video clips...")
        final_clips = [
            resized_clips[0].set_position((0, 0)),  # Top
            resized_clips[1].set_position((0, subframe_height)),  # Middle
            resized_clips[2].set_position((0, 2 * subframe_height)),  # Bottom
        ]

        # Combine the clips into one vertical video
        print("Combining video clips...")
        stacked_video = CompositeVideoClip(final_clips, size=(frame_width, frame_height))

        # Use the audio from the middle video
        print("Adding audio from the middle video...")
        stacked_video = stacked_video.set_audio(resized_clips[1].audio)

        # Write the final video to the output file
        print(f"Writing output video to {output_file}...")
        stacked_video.write_videofile(output_file, codec="libx264", audio_codec="aac", fps=resized_clips[0].fps)

        print(f"Video created successfully: {output_file}")

    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    # Provide paths to three video files
    video_paths = [
        "./output/Tennis_Trivia_01.mp4",  # Top
        "./output/Tennis_Trivia_02.mp4",  # Middle (audio source)
        "./output/Tennis_Trivia_03.mp4",  # Bottom
    ]
    output_file = "./output/3in1-vertical.mp4"
    create_vertical_video_with_audio(video_paths, output_file)
