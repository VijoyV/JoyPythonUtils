import speech_recognition as sr
from pydub import AudioSegment
import json
import time
import logging
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
import os
from pysrt import SubRipFile, SubRipItem, SubRipTime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

input_mp3 = config['input_mp3']
audio_language = config['audio_language']
image_for_video = config['image_for_video']
output_mp4 = config['output_mp4']
srt_filename = config.get('srt_filename', input_mp3.replace('.mp3', '.srt'))  # Default to .mp3 name if not provided
video_width, video_height = config['video_dimensions']
font_path = config.get('font_path', None)  # Specify a Malayalam font path

# Create temp directory for intermediate images
temp_dir = './temp'
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)

# Log the start of the process
logging.info("Starting the speech-to-video process.")
process_start_time = time.time()

# Step 1: Convert Speech to Text (SRT)
logging.info("Converting .mp3 to .wav for compatibility...")
audio = AudioSegment.from_mp3(input_mp3)
audio.export("temp_audio.wav", format="wav")
audio_duration = len(audio) / 1000  # Convert audio duration from ms to seconds
logging.info(f"Audio duration: {audio_duration:.2f} seconds.")

recognizer = sr.Recognizer()

# Recognize speech using Google Speech Recognition
text = None
with sr.AudioFile('temp_audio.wav') as source:
    audio_data = recognizer.record(source)

    try:
        logging.info("Recognizing speech using Google Speech Recognition...")
        text = recognizer.recognize_google(audio_data, language=audio_language)
        logging.info(f"Speech recognition successful. Extracted text: {text[:100]}...")
    except sr.UnknownValueError:
        logging.error("Google Speech Recognition could not understand audio")
        exit(1)
    except sr.RequestError as e:
        logging.error(f"Could not request results from Google Speech Recognition service; {e}")
        exit(1)

# If recognition was unsuccessful, stop the process
if not text:
    logging.error("No speech was recognized. Exiting.")
    exit(1)

# Step 2: Generate and save the .srt file
logging.info(f"Generating .srt file: {srt_filename}...")

srt_file = SubRipFile()
words = text.split()
chunk_size = 10  # Number of words per subtitle
num_chunks = len(words) // chunk_size
time_per_chunk = audio_duration / (num_chunks + 1)  # Divide by total number of chunks plus one to prevent overshooting


# Helper function to convert seconds to SubRipTime
def seconds_to_srt_time(seconds):
    milliseconds = int((seconds - int(seconds)) * 1000)
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return SubRipTime(hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)


# Loop through the text in chunks and assign proper timings
for i in range(0, len(words), chunk_size):
    start_time_seconds = i // chunk_size * time_per_chunk
    end_time_seconds = start_time_seconds + time_per_chunk

    # Prevent overshooting the total audio duration
    if end_time_seconds > audio_duration:
        end_time_seconds = audio_duration

    # Ensure the last chunk is not empty
    if i + chunk_size > len(words):
        chunk_size = len(words) - i

    subtitle_start_time = seconds_to_srt_time(start_time_seconds)
    subtitle_end_time = seconds_to_srt_time(end_time_seconds)
    srt_item = SubRipItem(i // chunk_size, subtitle_start_time, subtitle_end_time, ' '.join(words[i:i + chunk_size]))
    srt_file.append(srt_item)

# Save the SRT file
srt_file.save(srt_filename, encoding='utf-8')
logging.info(f".srt file saved to {srt_filename}.")


# Step 3: Render Malayalam Text on Image
def render_text_on_image(image_path, text, output_image_path):
    """Draws the Malayalam text onto the image using Pillow"""
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype(font_path, 40) if font_path else ImageFont.load_default()

    # Split text into multiple lines to fit within the image width
    image_width, image_height = img.size
    max_text_width = image_width - 40  # Padding from the sides
    lines = []
    current_line = ""
    for word in text.split():
        test_line = current_line + " " + word if current_line else word
        test_width, _ = draw.textbbox((0, 0), test_line, font=font)[2:4]
        if test_width <= max_text_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)

    # Position the text in the lower part of the image
    text_height = len(lines) * 50  # Approximate height per line
    y_position = (image_height - text_height) // 2 + 200  # Adjust this value for positioning

    for line in lines:
        text_width, _ = draw.textbbox((0, 0), line, font=font)[2:4]
        x_position = (image_width - text_width) // 2
        draw.text((x_position, y_position), line, font=font, fill="white")
        y_position += 50

    img.save(output_image_path)
    logging.info(f"Text rendered on image and saved to {output_image_path}")


# Step 4: Generate Image Clips for Each Subtitle
srt_data = SubRipFile.open(srt_filename)
image_clips = []

for i, item in enumerate(srt_data):
    # Get the start and end times in seconds for each subtitle
    start_seconds = item.start.ordinal / 1000.0
    end_seconds = item.end.ordinal / 1000.0

    # Render text for each subtitle on the image and save in ./temp directory
    output_image_with_text = os.path.join(temp_dir, f'temp_image_with_text_{i}.png')
    render_text_on_image(image_for_video, item.text, output_image_with_text)

    # Create an ImageClip for the rendered image with the correct duration
    duration = end_seconds - start_seconds
    if duration <= 0:
        duration = 1.0  # Ensure that each image has at least 1 second of duration

    image_clip = ImageClip(output_image_with_text).set_duration(duration).resize(newsize=(video_width, video_height))

    # Append to the list of image clips
    image_clips.append(image_clip)

    # Log when each image clip is created and its duration
    logging.info(
        f"Image {i} with text from {start_seconds:.2f}s to {end_seconds:.2f}s (duration: {duration:.2f}s) added to the video.")

# Step 5: Concatenate Image Clips and Add Audio
logging.info("Loading audio and creating final video...")

try:
    audio_clip = AudioFileClip(input_mp3)

    # Concatenate all image clips
    final_video = concatenate_videoclips(image_clips).set_audio(audio_clip)

    # Ensure the video ends exactly when the audio ends
    final_video = final_video.set_duration(audio_clip.duration)

    final_video.write_videofile(output_mp4, fps=24, codec='libx264', threads=4)
    logging.info(f"Video creation complete. Output file: {output_mp4}")
except Exception as e:
    logging.error(f"Error during video creation: {e}")
    exit(1)

# Log total time taken as float subtraction (corrected)
end_time = time.time()
total_time = end_time - process_start_time
logging.info(f"Total time taken: {total_time:.2f} seconds.")
