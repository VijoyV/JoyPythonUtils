import json
import logging
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from pydub import AudioSegment
import moviepy.editor as mp
import textwrap
import os
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message=s)')

def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)

def wrap_text(text, wrap_width, font, draw):
    lines = []
    words = text.split()
    line = ""

    for word in words:
        test_line = line + word + " "
        width, _ = font.getsize(test_line)
        if width <= wrap_width:
            line = test_line
        else:
            lines.append(line)
            line = word + " "
    lines.append(line)
    return lines

def generate_audio_from_text(text, speed, config):
    print("Text being sent to gTTS:", text)
    try:
        output_audio_path = os.path.join(config["output_dir"], "output_audio.mp3")

        print("Generating audio...")
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(output_audio_path)

        if not os.path.exists(output_audio_path):
            print("Error: Audio file was not created.")
            return 0

        print(f"Audio created successfully at {output_audio_path}")

        # Load audio
        audio = AudioSegment.from_mp3(output_audio_path)

        # Log the duration of the generated audio
        audio_duration = audio.duration_seconds
        print(f"Audio duration: {audio_duration} seconds.")

        return audio_duration
    except Exception as e:
        print(f"Error generating audio: {e}")
        return 0

def generate_frame(image, draw, text_lines, font, text_color, highlight_color, x, y, word_idx):
    current_word = 0  # Word counter

    # Get the height of a line using textbbox
    line_height = draw.textbbox((x, y), "A", font=font)[3] - draw.textbbox((x, y), "A", font=font)[1]

    for line in text_lines:
        x_position = x  # Reset x position for each line
        for word in line.split():
            # Highlight the current word, otherwise set normal text color
            color = highlight_color if current_word == word_idx else text_color
            draw.text((x_position, y), word, font=font, fill=color)

            # Update x position by the width of the word using textbbox
            word_width = draw.textbbox((x_position, y), word + " ", font=font)[2] - \
                         draw.textbbox((x_position, y), word + " ", font=font)[0]
            x_position += word_width  # Add width of word plus space

            current_word += 1

        # After processing a line, move y position down by the line height
        y += line_height + 60

    return image

def create_video_with_text(config):
    try:
        # Load the configuration
        image_path = config["image_path"]
        output_video = config["output_video"]
        font_path = config["font_path"]
        font_size = config["font_size"]
        wrap_width = config["wrap_width"]
        text_color = config["text_color"]
        highlight_color = config["highlight_color"]
        fps = config["fps"]
        output_audio_path = os.path.join(config["output_dir"], "output_audio.mp3")

        # Load image and text
        image = Image.open(image_path).convert("RGBA")
        image_width, image_height = image.size

        # Scale image for higher resolution
        scale_factor = 2  # Scale image 2x for better text rendering
        image = image.resize((image_width * scale_factor, image_height * scale_factor), Image.LANCZOS)
        draw = ImageDraw.Draw(image)

        # Load the text from file
        with open(config["text_file"], 'r') as f:
            text = f.read()

        # Debugging: print the loaded text content
        print(f"Text content loaded from {config['text_file']}:")
        print(text)

        # Load font with larger size for higher resolution
        font = ImageFont.truetype(font_path, font_size * scale_factor)

        # Wrap text to fit the image width
        text_lines = textwrap.wrap(text, width=wrap_width)
        total_words = len(text.split())

        # Generate or reuse audio and get duration
        audio_duration = generate_audio_from_text(text, config["audio_speed"], config)
        if audio_duration == 0:
            print("Failed to generate audio, exiting.")
            return

        # Calculate the duration per word
        word_duration = audio_duration / total_words

        # Initialize MoviePy
        frames = []

        x, y = 50, 50  # Initial text position
        time_per_frame = 1 / fps
        total_frames = int(audio_duration * fps)

        # Debugging: Log total frames and total words
        print(f"Total frames to be generated: {total_frames}")
        print(f"Total words to be processed: {total_words}")

        # Generate each frame for the video
        for frame_num in range(total_frames):
            time_elapsed = frame_num * time_per_frame
            current_word_idx = min(int((time_elapsed + 0.2) / word_duration), total_words - 1)

            frame_image = generate_frame(image.copy(), draw, text_lines, font, text_color, highlight_color, x, y,
                                         current_word_idx)

            # Downscale frame back to original size before appending
            frame_image = frame_image.resize((image_width, image_height), Image.LANCZOS)

            # Convert the frame to a NumPy array and append it
            frames.append(np.array(frame_image.convert("RGB")))  # Convert to NumPy array before appending

            # Log frame creation
            if frame_num % 50 == 0 or frame_num == total_frames - 1:
                print(f"Processed frame {frame_num}/{total_frames}")

        # Check if frames were generated
        if not frames:
            print("No frames were generated, exiting.")
            return

        # Create video clip from frames
        video_clip = mp.ImageSequenceClip(frames, fps=fps)

        # Add the audio
        audio_clip = mp.AudioFileClip(output_audio_path)

        # Set the audio to the video and export the final video
        final_video = video_clip.set_audio(audio_clip)

        # Ensure the video duration matches the audio duration
        final_video = final_video.set_duration(audio_duration)

        # High-quality video export
        final_video.write_videofile(output_video, codec="libx264", bitrate="5000k", preset="slow")

        print("Video creation complete.")

    except Exception as e:
        print(f"Error during video creation: {e}")

def main():
    try:
        # Load config
        config = load_config("./config/image_to_video.json")

        # Create video with synchronized text writing
        create_video_with_text(config)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
