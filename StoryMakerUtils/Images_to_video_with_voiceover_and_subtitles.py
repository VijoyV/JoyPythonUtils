"""
Explanation of Changes:

Splitting Subtitles:
The split_text function splits the text into multiple lines based on full stops. Each line is treated as a separate line of the subtitle.

Displaying Subtitles:
The add_subtitle_to_image function now loops through each line of text and places them on the image. The lines are vertically spaced to avoid overlap.

Stretching Images:
The resize(video_size) method in the ImageClip creation stretches the image to fit the full screen (1920x1080 in this case). Adjust video_size as needed for different screen resolutions.

Running the Script:
Update the script with your specific paths and settings, then run it as usual.
The output video will have each image stretched to full screen with properly formatted, multiline subtitles.

"""
import moviepy.editor as mpy
from gtts import gTTS
import os
from PIL import Image, ImageDraw, ImageFont

# Configuration
image_folder = 'C:\\SocialMediaWorkshop\\FoxAndCrow_4_Story\\Images'  # Replace with the folder containing your images
voice_text_file = 'C:\\SocialMediaWorkshop\\FoxAndCrow_4_Story\\VoiceOverText\\voiceover.txt'  # Replace with the path to your text file
output_audio_folder = 'C:\\SocialMediaWorkshop\\FoxAndCrow_4_Story\\GeneratedAudio'  # Replace with the folder to save generated audio files
output_video_path = 'C:\\SocialMediaWorkshop\\FoxAndCrow_4_Story\\FoxAndCrowStory.mp4'  # Replace with the desired output video path

duration_per_image = 14  # Duration to display each image in seconds
font_size = 40  # Font size for subtitles
font_color = 'yellow'  # Font color for subtitles
subtitles_position = ('center', 'bottom')  # Position of subtitles on the video

# Ensure audio folder exists
os.makedirs(output_audio_folder, exist_ok=True)

# Read the voice-over text from the text file
with open(voice_text_file, 'r') as file:
    voiceover_texts = [line.strip() for line in file.readlines()]

print('voiceover_texts = ', voiceover_texts)

# Get list of image files
image_files = sorted(
    [os.path.join(image_folder, img) for img in os.listdir(image_folder) if img.endswith(('png', 'jpg', 'jpeg'))])

print('image_files = ', image_files)

# Ensure there are as many text entries as there are images
if len(voiceover_texts) != len(image_files):
    raise ValueError("The number of text entries must match the number of images.")


# Function to add subtitles to an image
def add_subtitle_to_image(image_path, text, font_size, font_color):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    # Load a font
    font = ImageFont.truetype("arial.ttf", font_size)

    # Calculate text size and position using textbbox
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

    width, height = image.size

    if subtitles_position[0] == 'center':
        x_position = (width - text_width) / 2
    elif subtitles_position[0] == 'left':
        x_position = 10
    elif subtitles_position[0] == 'right':
        x_position = width - text_width - 10

    if subtitles_position[1] == 'bottom':
        y_position = height - text_height - 10
    elif subtitles_position[1] == 'top':
        y_position = 10
    elif subtitles_position[1] == 'center':
        y_position = (height - text_height) / 2

    # Add text to image
    draw.text((x_position, y_position), text, font=font, fill=font_color)

    # Save the image with subtitles
    subtitle_image_path = image_path.replace(".jpg", "_subtitled.jpg")
    image.save(subtitle_image_path)

    return subtitle_image_path


# Generate voice-over audio files and create video clips
video_clips = []
for i, (image_path, text) in enumerate(zip(image_files, voiceover_texts)):
    # Generate the voice-over audio
    tts = gTTS(text=text, lang='en')
    audio_path = os.path.join(output_audio_folder, f"voiceover_{i + 1}.mp3")
    tts.save(audio_path)

    # Add subtitles to the image
    subtitle_image_path = add_subtitle_to_image(image_path, text, font_size, font_color)

    # Load the generated audio clip
    audio_clip = mpy.AudioFileClip(audio_path)

    # Create the image clip with the subtitled image
    img_clip = mpy.ImageClip(subtitle_image_path).set_duration(duration_per_image).set_audio(audio_clip)

    video_clips.append(img_clip)

# Concatenate all image clips into a single video
final_video = mpy.concatenate_videoclips(video_clips, method="compose")

# Export the final video
final_video.write_videofile(output_video_path, fps=24)

print(f"Video created successfully with subtitles at {output_video_path}!")

"""
Script Summary:

Configuration:
Defines paths to images, text file, audio folder, and the final video output.
Specifies the duration each image should be displayed, the font size and color for subtitles, and the position of subtitles.

Reading Input Files:
Reads the voice-over text lines from the specified text file.
Retrieves and sorts image files from the given folder.

Validation:
Ensures the number of text entries matches the number of images.

Subtitles and Voice-Over Generation:
Uses the gTTS library to generate an audio file for each line of text.
Adds subtitles to each image using Pillow.
Creates a video clip for each image with the corresponding voice-over and subtitles.

Video Creation:
Concatenates all the video clips into a single video.
Exports the final video with the specified frames per second (fps).

Output:
The script will generate a video where each image is displayed for the specified duration with corresponding subtitles and voice-over, 
and save it at the specified output_video_path.

"""