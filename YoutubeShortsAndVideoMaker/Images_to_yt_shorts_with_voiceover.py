import moviepy.editor as mpy
from gtts import gTTS
import os
import json
from concurrent.futures import ThreadPoolExecutor
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Start timing
start_time = time.time()

# Load configuration from config.json
logging.info("Loading configuration from config.json")
with open('config/Images_to_yt_shorts_with_voiceover.json', 'r') as f:
    config = json.load(f)

image_folder = config['image_folder']
voice_text_file = config['voice_text_file']
output_audio_folder = config['output_audio_folder']
output_video_path = config['output_video_path']
background_music_path = config['background_music_path']
durations_per_image = config['durations_per_image']
video_size = tuple(config['video_size'])  # Video size (for vertical orientation)
background_music_volume = config['background_music_volume']

# Ensure audio folder exists
logging.info(f"Ensuring output audio folder exists: {output_audio_folder}")
os.makedirs(output_audio_folder, exist_ok=True)

# Read the voice-over text from the text file with UTF-8 encoding to avoid encoding errors
logging.info(f"Reading voiceover text from {voice_text_file}")
with open(voice_text_file, 'r', encoding='utf-8') as file:
    voiceover_texts = [line.strip() for line in file.readlines()]

# Get list of image files
logging.info(f"Fetching image files from {image_folder}")
image_files = sorted([os.path.join(image_folder, img) for img in os.listdir(image_folder) if img.endswith(('webp', 'PNG', 'jpg', 'jpeg'))])

# Ensure there are as many text entries as there are images and durations
logging.info(f"Validating the number of text entries, image files, and durations")
if len(voiceover_texts) != len(image_files) or len(durations_per_image) != len(image_files):
    raise ValueError("The number of text entries, image files, and durations must match.")

# Function to generate voiceover and process images in parallel
def process_image_audio(i, image_path, text, duration):
    logging.info(f"Processing image {i+1}/{len(image_files)}: {image_path}")
    # Generate the voice-over audio only if it doesn't already exist
    audio_path = os.path.join(output_audio_folder, f"voiceover_{i + 1}.mp3")
    if not os.path.exists(audio_path):
        logging.info(f"Generating voiceover audio for image {i+1}")
        tts = gTTS(text=text, lang='en')
        tts.save(audio_path)

    # Load the generated audio clip
    audio_clip = mpy.AudioFileClip(audio_path)

    # Create the image clip and resize to vertical (portrait) mode
    img_clip = mpy.ImageClip(image_path).set_duration(duration).set_audio(audio_clip)
    img_clip = img_clip.resize(video_size)  # Resize to vertical (portrait) mode

    return img_clip

# Parallelize image and audio processing using ThreadPoolExecutor
logging.info(f"Processing images and audio clips in parallel")
with ThreadPoolExecutor() as executor:
    video_clips = list(executor.map(process_image_audio, range(len(image_files)), image_files, voiceover_texts, durations_per_image))

# Concatenate all image clips into a single video
logging.info("Concatenating image clips into a single video")
final_video = mpy.concatenate_videoclips(video_clips, method="compose")

# Load and set the background music
logging.info(f"Loading background music from {background_music_path}")
background_music = mpy.AudioFileClip(background_music_path).subclip(0, final_video.duration)
# background_music = background_music.volumex(background_music_volume)  # Adjust the volume once
background_music = background_music.audio_fadeout(3).volumex(background_music_volume)

# Set the combined audio (background music + voice-over)
logging.info("Setting combined audio (background music + voice-over)")
final_audio = mpy.CompositeAudioClip([background_music, final_video.audio])
final_video = final_video.set_audio(final_audio)

# Export the final video with optimized multithreading
logging.info(f"Exporting the final video to {output_video_path}")
final_video.write_videofile(output_video_path, fps=24, threads=8)

# Calculate total processing time
end_time = time.time()
total_time = end_time - start_time
logging.info(f"Video created successfully with background music at {output_video_path}!")
logging.info(f"Total processing time: {total_time:.2f} seconds")
