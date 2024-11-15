import json
import os
from moviepy.editor import ImageClip, AudioFileClip, afx
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load config from config.json
with open('./config/config-07.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

slides = config['slides']

# Step 1: Process each slide from config and generate individual mp4 files
for i, slide in enumerate(slides):
    image_path = slide['image']
    audio_path = slide['mp3']
    output_mp4 = slide['output_mp4']

    try:
        # Create an AudioFileClip for each audio
        audio_clip = AudioFileClip(audio_path)
        audio_duration = audio_clip.duration

        # Apply a fade-out effect to the last second of the audio using afx
        audio_clip = afx.audio_fadeout(audio_clip, 0.5)

        # Create an ImageClip for each image with the same duration as the audio
        image_clip = ImageClip(image_path).set_duration(audio_duration).set_audio(audio_clip)

        # Export the individual slide video to the specified MP4 file
        image_clip.write_videofile(output_mp4, fps=24, codec='libx264', threads=4)
        logging.info(f"Created video {output_mp4} with duration {audio_duration:.2f} seconds for Slide {i + 1}.")

        # Verify if the video duration matches the audio duration
        video_duration = image_clip.duration
        if abs(video_duration - audio_duration) > 0.01:  # Allow for a small floating-point discrepancy
            logging.warning(f"Duration mismatch for Slide {i + 1}: MP3 duration {audio_duration:.2f}s, MP4 duration {video_duration:.2f}s.")

    except Exception as e:
        logging.error(f"Error processing Slide {i + 1}: {e}")
        exit(1)
