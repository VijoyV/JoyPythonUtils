import logging
import warnings
from moviepy.editor import VideoFileClip, concatenate_videoclips, afx
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Suppress specific MoviePy warnings
warnings.filterwarnings("ignore", category=UserWarning, module="moviepy")


def apply_fadeout(video, duration=2):
    """Apply fade-out effect to the last 'duration' seconds of the video."""
    return video.fadeout(duration)


def concatenate_videos(file1, file2, file3, output_file, repeat_count=10):
    try:
        logging.info('Loading video files...')
        video1 = VideoFileClip(file1)
        video2 = VideoFileClip(file2)
        video3 = VideoFileClip(file3)

        # Apply fade-out to each video clip to prevent unwanted sound at the end
        video1 = apply_fadeout(video1)
        video2 = apply_fadeout(video2)
        video3 = apply_fadeout(video3)

        # Pre-export video2 to avoid re-encoding multiple times
        temp_video2_path = "./temp/video2_repeated.mp4"
        if not os.path.exists("./temp"):
            os.makedirs("./temp")

        video2.write_videofile(temp_video2_path, codec="libx264", audio_codec="aac", bitrate="5000k", preset="fast")
        video2_repeated_clip = VideoFileClip(temp_video2_path)

        # Create a list containing references to pre-encoded video2
        video2_repeated_03_times = [video2_repeated_clip] * 3
        video2_repeated_10_times = [video2_repeated_clip] * repeat_count

        # Function to repeat video1 + video2_repeated + video3 pattern
        def repeat_pattern(video1, video2_repeated, video3, times):
            clips = []
            for _ in range(times):
                clips.extend([video1] + video2_repeated + [video3])
            return clips

        # Create the final concatenated video
        final_clips = [video1] + video2_repeated_03_times + [video3] + repeat_pattern(video1, video2_repeated_10_times,
                                                                                      video3, 5)

        logging.info('Concatenating video clips...')
        final_video = concatenate_videoclips(final_clips, method="chain")

        # Export the final concatenated video
        logging.info(f'Exporting final video to {output_file}...')
        final_video.write_videofile(output_file, codec="libx264", audio_codec="aac", bitrate="5000k", preset="fast")
        logging.info(f"Successfully saved final video: {output_file}")

        # Clean up temporary files
        video2_repeated_clip.close()
        os.remove(temp_video2_path)

    except Exception as e:
        logging.error(f"Error processing video files: {e}")


if __name__ == "__main__":
    file1 = "./input/Swargasthanaya.mp4"  # Replace with the path to your video1.mp4
    file2 = "./input/NanmaNiranjaMariyame.mp4"  # Replace with the path to your video2.mp4
    file3 = "./input/Sthuthi.mp4"  # Replace with the path to your video3.mp4
    output_file = "./output/JapamalaVideo.mp4"  # Desired output file name

    # Concatenate and save the final video with fade-out applied
    concatenate_videos(file1, file2, file3, output_file, repeat_count=10)
