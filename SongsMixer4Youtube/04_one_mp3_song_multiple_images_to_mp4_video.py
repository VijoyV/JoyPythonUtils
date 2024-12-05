import os
import json
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

def create_video_with_images_and_audio(config_file):
    # Load configuration
    with open(config_file, 'r') as f:
        config = json.load(f)

    mp3_file = config.get("mp3_file")
    output_video = config.get("output_video")
    image_settings = config.get("images", [])

    # Validate MP3 file
    if not os.path.exists(mp3_file):
        print(f"Error: MP3 file '{mp3_file}' not found.")
        return

    # Validate image files
    for image_setting in image_settings:
        if not os.path.exists(image_setting["image"]):
            print(f"Error: Image file '{image_setting['image']}' not found.")
            return

    print("Creating video...")

    # Create audio clip
    audio_clip = AudioFileClip(mp3_file)
    song_duration = audio_clip.duration

    # Create image clips based on timings
    video_clips = []
    for i, image_setting in enumerate(image_settings):
        image_path = image_setting["image"]
        start_time = image_setting["start_time"]

        # Calculate duration for the current image
        if i + 1 < len(image_settings):
            next_start_time = image_settings[i + 1]["start_time"]
            duration = max(0, next_start_time - start_time)
        else:
            duration = max(0, song_duration - start_time)

        if duration > 0:
            image_clip = ImageClip(image_path, duration=duration).set_start(start_time)
            video_clips.append(image_clip)

    # Concatenate all image clips
    final_video = concatenate_videoclips(video_clips, method="compose").set_audio(audio_clip)

    # Write final video to file
    final_video.write_videofile(output_video, fps=24)
    print(f"Video created successfully: {output_video}")

if __name__ == "__main__":
    config_file = "./04_song_images_mapping.json"  # Path to the configuration file
    create_video_with_images_and_audio(config_file)
