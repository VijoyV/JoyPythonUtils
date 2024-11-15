import json
import os
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load config from config.json
with open('./config/config-05.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

input_mp3 = config['input_mp3']
output_mp4 = config['output_mp4']
slides = config['slides']

# Create temp directory if needed (not really necessary unless doing intermediate processing)
temp_dir = './temp'
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)

# Step 1: Process each slide from config and generate image clips
image_clips = []

for i, slide in enumerate(slides):
    image_path = slide['image']
    duration = slide['duration']  # Duration of the slide

    # Create an ImageClip for each image with the correct duration
    image_clip = ImageClip(image_path).set_duration(duration)
    image_clips.append(image_clip)

    logging.info(f"Slide {i+1} with image {image_path} will be shown for {duration} seconds.")

# Step 2: Concatenate image clips and add audio
logging.info("Loading audio and creating final video...")

try:
    audio_clip = AudioFileClip(input_mp3)
    logging.info(f"Audio duration: {audio_clip.duration:.2f} seconds")

    # Concatenate all image clips
    final_video = concatenate_videoclips(image_clips)
    logging.info(f"Video duration before extending: {final_video.duration:.2f} seconds")
    logging.info(f"Number of image clips: {len(image_clips)}")

    # Ensure the video ends exactly when the audio ends
    if final_video.duration < audio_clip.duration:
        logging.info("Extending the last slide to cover remaining audio duration.")
        if len(image_clips) > 0:  # Ensure there are clips to extend
            extra_duration = audio_clip.duration - final_video.duration
            new_duration = image_clips[-1].duration + extra_duration
            logging.info(f"Extending last slide from {image_clips[-1].duration:.2f}s to {new_duration:.2f}s")
            # Update the duration of the last clip
            image_clips[-1] = image_clips[-1].set_duration(new_duration)
            # Re-concatenate the clips
            final_video = concatenate_videoclips(image_clips)
        else:
            logging.error("No image clips available to extend!")
            exit(1)
    else:
        logging.info("No need to extend the last slide.")

    # Set audio and duration
    final_video = final_video.set_audio(audio_clip).set_duration(audio_clip.duration)

    # Step 3: Export the final video to MP4
    final_video.write_videofile(output_mp4, fps=24, codec='libx264', threads=4)
    logging.info(f"Video creation complete. Output file: {output_mp4}")

except IndexError as e:
    logging.error(f"IndexError: {e}")
    exit(1)
except Exception as e:
    logging.error(f"An unexpected error occurred: {e}")
    exit(1)
