import json
import os
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load config from config.json
with open('./config/config-06.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

output_mp4 = config['output_mp4']
slides = config['slides']

# Create temp directory if needed (for intermediate processing, if necessary)
temp_dir = './temp'
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)

# Step 1: Process each slide from config and generate image/audio clips
video_clips = []

for i, slide in enumerate(slides):
    image_path = slide['image']
    audio_path = slide['mp3']

    # Create an AudioFileClip for each audio
    try:
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration
    except Exception as e:
        logging.error(f"Error processing audio file {audio_path}: {e}")
        exit(1)

    # Create an ImageClip for each image with the same duration as the audio
    try:
        image_clip = ImageClip(image_path).set_duration(duration).set_audio(audio_clip)
        video_clips.append(image_clip)
        logging.info(f"Slide {i+1} with image {image_path} and audio {audio_path} will be shown for {duration:.2f} seconds.")
    except Exception as e:
        logging.error(f"Error processing image file {image_path}: {e}")
        exit(1)

# Step 2: Concatenate all image/audio clips into a final video
logging.info("Concatenating video clips...")

try:
    final_video = concatenate_videoclips(video_clips)
    # Step 3: Export the final video to MP4
    final_video.write_videofile(output_mp4, fps=24, codec='libx264', threads=4)
    logging.info(f"Video creation complete. Output file: {output_mp4}")
except Exception as e:
    logging.error(f"An unexpected error occurred during video concatenation: {e}")
    exit(1)
