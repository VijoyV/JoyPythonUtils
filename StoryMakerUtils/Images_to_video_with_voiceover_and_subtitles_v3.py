import moviepy.editor as mpy
from gtts import gTTS
import os
from PIL import Image, ImageDraw, ImageFont

# Configuration
# Replace with the folder containing your images
image_folder = 'C:\\SocialMediaWorkshop\\4_YoutubeChannel\\AesopFables_05_AntAndGrasshopper\\Images'
# Replace with the path to your text file
voice_text_file = 'C:\\SocialMediaWorkshop\\4_YoutubeChannel\\AesopFables_05_AntAndGrasshopper\\VoiceOverText\\voiceover.txt'
# Replace with the folder to save generated audio files
output_audio_folder = 'C:\\SocialMediaWorkshop\\4_YoutubeChannel\\AesopFables_05_AntAndGrasshopper\\GeneratedAudio'
# Replace with the desired output video path
output_video_path = 'C:\\SocialMediaWorkshop\\4_YoutubeChannel\\AesopFables_05_AntAndGrasshopper\\AntAndGrasshopper.mp4'
# Replace with the path to your background music file
background_music_path = 'C:\\SocialMediaWorkshop\\4_YoutubeChannel\\AesopFables_05_AntAndGrasshopper\\BackgroundMusic\\dreams.mp3'

# List of durations per image (in seconds)
durations_per_image = [7, 18, 14, 13, 12, 13, 15]  # Replace with the desired durations for each image

font_size = 32 # Font size for subtitles
font_color = 'white'  # Font color for subtitles
subtitles_position = ('center', 'bottom')  # Position of subtitles on the video
video_size = (1920, 1080)  # Target video size (Full HD)
background_music_volume = 0.3  # Volume level for background music (0.0 to 1.0)

# Ensure audio folder exists
os.makedirs(output_audio_folder, exist_ok=True)

# Read the voice-over text from the text file
with open(voice_text_file, 'r') as file:
    voiceover_texts = [line.strip() for line in file.readlines()]

print('voiceover_texts = ', voiceover_texts)

# Get list of image files
image_files = sorted(
    [os.path.join(image_folder, img) for img in os.listdir(image_folder) if img.endswith(('webp'))])

# img.endswith(('png', 'webp', 'jpg', 'jpeg')
print('image_files = ', image_files)

# Ensure there are as many text entries as there are images and durations
if len(voiceover_texts) != len(image_files) or len(durations_per_image) != len(image_files):
    raise ValueError("The number of text entries, image files, and durations must match.")

# Function to split text into multiple lines based on full stops
def split_text(text):
    sentences = text.split('.')
    # Remove any empty strings and add periods back except for the last sentence
    return [sentence.strip() + '.' if i < len(sentences) - 1 else sentence.strip()
            for i, sentence in enumerate(sentences) if sentence.strip()]

 # Add text with background color to the image
def add_subtitle_to_image(image_path, text_lines, font_size, font_color, bg_color='grey'):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    # Load a font
    font = ImageFont.truetype("arial.ttf", font_size)

    width, height = image.size

    # Add each line of text to the image
    for i, line in enumerate(text_lines):
        text_bbox = draw.textbbox((0, 0), line, font=font)
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

        if subtitles_position[0] == 'center':
            x_position = (width - text_width) / 2
        elif subtitles_position[0] == 'left':
            x_position = 10
        elif subtitles_position[0] == 'right':
            x_position = width - text_width - 10

        if subtitles_position[1] == 'bottom':
            y_position = height - text_height - 10 - (len(text_lines) - i - 1) * (text_height + 5)
        elif subtitles_position[1] == 'top':
            y_position = 10 + i * (text_height + 5)
        elif subtitles_position[1] == 'center':
            y_position = (height - text_height) / 2 + i * (text_height + 5)

        # Draw the background rectangle
        draw.rectangle([x_position-5, y_position-5, x_position + text_width + 5, y_position + text_height + 5], fill=bg_color)

        # Add text to image
        draw.text((x_position, y_position), line, font=font, fill=font_color)

    # Save the image with subtitles
    subtitle_image_path = image_path.replace(".webp", "_subtitled.webp")
    image.save(subtitle_image_path)

    return subtitle_image_path

# Generate voice-over audio files and create video clips
video_clips = []
total_duration = 0  # To calculate the total duration of the video
for i, (image_path, text, duration) in enumerate(zip(image_files, voiceover_texts, durations_per_image)):
    # Generate the voice-over audio
    tts = gTTS(text=text, lang='en')
    audio_path = os.path.join(output_audio_folder, f"voiceover_{i + 1}.mp3")
    tts.save(audio_path)

    # Split the text into multiple lines based on full stops
    text_lines = split_text(text)

    # Add subtitles to the image
    subtitle_image_path = add_subtitle_to_image(image_path, text_lines, font_size, font_color)

    # Load the generated audio clip
    audio_clip = mpy.AudioFileClip(audio_path)

    # Create the image clip with the subtitled image and stretch to full screen
    img_clip = mpy.ImageClip(subtitle_image_path).set_duration(duration).set_audio(audio_clip)
    img_clip = img_clip.resize(video_size)  # Resize to full screen

    video_clips.append(img_clip)
    total_duration += duration  # Add duration to total duration

# Concatenate all image clips into a single video
final_video = mpy.concatenate_videoclips(video_clips, method="compose")

# Load and set the background music
background_music = mpy.AudioFileClip(background_music_path).subclip(0, total_duration)
background_music = background_music.volumex(background_music_volume)  # Adjust the volume

# Set the combined audio (background music + voice-over)
final_audio = mpy.CompositeAudioClip([background_music.volumex(background_music_volume), final_video.audio])
final_video = final_video.set_audio(final_audio)

# Export the final video
final_video.write_videofile(output_video_path, fps=24)

print(f"Video created successfully with background music at {output_video_path}!")
