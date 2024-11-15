from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
import os
import json
import logging
from pysrt import SubRipFile

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

input_mp3 = config['input_mp3']
image_for_video = config['image_for_video']
output_mp4 = config['output_mp4']
srt_filename = config['srt_filename']
video_width, video_height = config['video_dimensions']
font_path = config.get('font_path', None)  # Specify a Malayalam font path if available

# Create temp directory for intermediate images
temp_dir = './temp'
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)

# Step 4: Render text on image
def render_text_on_image(image_path, text, output_image_path):
    """Draws the subtitle text onto the image using Pillow"""
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, 40) if font_path else ImageFont.load_default()

    image_width, image_height = img.size
    max_text_width = image_width - 40  # Padding from the sides
    lines = []
    current_line = ""

    # Split text into multiple lines to fit within the image width
    for word in text.split():
        test_line = current_line + " " + word if current_line else word
        test_width, _ = draw.textbbox((0, 0), test_line, font=font)[2:4]
        if test_width <= max_text_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)

    # Position the text at the lower part of the image
    text_height = len(lines) * 50
    y_position = (image_height - text_height) // 2 + 200  # Adjust value as needed

    for line in lines:
        text_width, _ = draw.textbbox((0, 0), line, font=font)[2:4]
        x_position = (image_width - text_width) // 2
        draw.text((x_position, y_position), line, font=font, fill="white")
        y_position += 50

    img.save(output_image_path)
    logging.info(f"Text rendered on image and saved to {output_image_path}")

# Step 5: Generate image clips for each subtitle
srt_data = SubRipFile.open(srt_filename)
image_clips = []

for i, item in enumerate(srt_data):
    start_seconds = item.start.ordinal / 1000.0
    end_seconds = item.end.ordinal / 1000.0

    # Render text for each subtitle on the image and save in the temp directory
    output_image_with_text = os.path.join(temp_dir, f'temp_image_with_text_{i}.png')
    render_text_on_image(image_for_video, item.text, output_image_with_text)

    # Create an ImageClip for the rendered image with the correct duration
    duration = end_seconds - start_seconds
    if duration <= 0:
        duration = 1.0  # Ensure each image has at least 1 second duration

    image_clip = ImageClip(output_image_with_text).set_duration(duration).resize(newsize=(video_width, video_height))

    # Append to the list of image clips
    image_clips.append(image_clip)

    logging.info(f"Image {i} with text from {start_seconds:.2f}s to {end_seconds:.2f}s (duration: {duration:.2f}s) added to video.")

# Step 6: Concatenate image clips and add audio
logging.info("Loading audio and creating final video...")

try:
    audio_clip = AudioFileClip(input_mp3)

    # Concatenate all image clips
    final_video = concatenate_videoclips(image_clips).set_audio(audio_clip)

    # Ensure the video ends exactly when the audio ends
    final_video = final_video.set_duration(audio_clip.duration)

    # Step 7: Export the video to MP4
    final_video.write_videofile(output_mp4, fps=24, codec='libx264', threads=4)
    logging.info(f"Video creation complete. Output file: {output_mp4}")
except Exception as e:
    logging.error(f"Error during video creation: {e}")
    exit(1)
