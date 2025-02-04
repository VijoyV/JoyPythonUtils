import os
import json
from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    concatenate_videoclips,
)


def create_video_with_fade_effects(config_file, fade_duration=1):
    """
    Create a video combining an MP3 song and multiple images with specified timings and fade transitions.
    """
    # Load configuration
    with open(config_file, 'r') as f:
        config = json.load(f)

    mp3_file = config.get("mp3_file")
    output_video = config.get("output_video")
    image_settings = config.get("images", [])

    # Validate MP3 file
    if not os.path.exists(mp3_file):
        raise FileNotFoundError(f"Error: MP3 file '{mp3_file}' not found.")

    # Validate image files
    for image_setting in image_settings:
        if not os.path.exists(image_setting["image"]):
            raise FileNotFoundError(f"Error: Image file '{image_setting['image']}' not found.")

    print("Creating video...")

    # Create audio clip
    audio_clip = AudioFileClip(mp3_file)
    song_duration = audio_clip.duration

    print(f"MP3 Song Duration: {song_duration} seconds")

    # Create video clips with fade effects
    video_clips = []
    for i, image_setting in enumerate(image_settings):
        image_path = image_setting["image"]
        start_time = image_setting["start_time"]
        end_time = image_setting["end_time"]

        # Validate times
        if end_time <= start_time:
            raise ValueError(f"Invalid timing for image {image_path}: end_time must be greater than start_time.")

        # Calculate duration for the current clip
        duration = end_time - start_time

        # Create the image clip with fade effects
        image_clip = ImageClip(image_path, duration=duration)
        faded_clip = image_clip.fadein(fade_duration).fadeout(fade_duration)
        video_clips.append(faded_clip)

    # Concatenate all video clips
    final_video = concatenate_videoclips(video_clips, method="compose").set_audio(audio_clip)

    # Write the final video to a file
    final_video.write_videofile(output_video, fps=24, codec="libx264", audio_codec="aac")
    print(f"Video created successfully: {output_video}")


if __name__ == "__main__":
    config_file = "./04_song_images_mapping.json"
    try:
        create_video_with_fade_effects(config_file, fade_duration=1)
    except Exception as e:
        print(f"An error occurred: {e}")
