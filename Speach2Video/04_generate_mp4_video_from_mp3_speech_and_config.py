import json
import os
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load config from config.json
with open('./config/config-04.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

input_mp3 = config['input_mp3']
output_mp4 = config['output_mp4']
slides = config['slides']
video_width, video_height = config['video_dimensions']
font_path = config.get('font_path', 'NotoSansMalayalam-Regular.ttf')  # Default font path
font_size = config.get('font_size', 40)
font_color = config.get('font_color', 'white')

# Create temp directory for intermediate images
temp_dir = './temp'
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)

# Function to render text on image using Pillow
def render_text_on_image(image_path, text, output_image_path):
    """Draw the text onto an image using Pillow."""
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    # Load the font
    font = ImageFont.truetype(font_path, font_size)

    # Image dimensions
    image_width, image_height = img.size
    max_text_width = image_width - 40  # Padding from sides
    lines = []
    current_line = ""

    # Word wrapping logic
    for word in text.split():
        test_line = current_line + " " + word if current_line else word
        test_width, _ = draw.textbbox((0, 0), test_line, font=font)[2:4]
        if test_width <= max_text_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)

    # Position the text in the image
    text_height = len(lines) * (font_size + 10)
    y_position = (image_height - text_height) // 2 + 200

    for line in lines:
        text_width, _ = draw.textbbox((0, 0), line, font=font)[2:4]
        x_position = (image_width - text_width) // 2
        draw.text((x_position, y_position), line, font=font, fill=font_color)
        y_position += font_size + 10

    img.save(output_image_path)
    logging.info(f"Text rendered on image and saved to {output_image_path}")

# Step 1: Process each slide from config and generate image clips
image_clips = []

for i, slide in enumerate(slides):
    image_path = slide['image']
    text = slide['text']
    start_time = slide['from_time']  # mm:ss format
    end_time = slide['to_time']  # mm:ss format

    # Convert time to seconds
    start_seconds = int(start_time.split(':')[0]) * 60 + int(start_time.split(':')[1])
    end_seconds = int(end_time.split(':')[0]) * 60 + int(end_time.split(':')[1])
    duration = end_seconds - start_seconds

    # Render the text onto the image
    output_image_with_text = os.path.join(temp_dir, f'temp_image_with_text_{i}.png')
    render_text_on_image(image_path, text, output_image_with_text)

    # Create an ImageClip for the rendered image with the correct duration
    image_clip = ImageClip(output_image_with_text).set_duration(duration).resize(newsize=(video_width, video_height))

    # Append to the list of image clips
    image_clips.append(image_clip)
    logging.info(f"Slide {i+1} from {start_time} to {end_time} (duration: {duration} seconds) added to video.")

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
