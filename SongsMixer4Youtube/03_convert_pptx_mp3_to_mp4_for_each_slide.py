import os
import json
import win32com.client
from mutagen.mp3 import MP3
from moviepy.editor import ImageClip, AudioFileClip


# Step 1: Export PPT slides as images using win32com.client PowerPoint COM interface
def ppt_to_images(ppt_path, output_dir):
    ppt_path = os.path.abspath(ppt_path)  # Convert to absolute path
    output_dir = os.path.abspath(output_dir)  # Convert to absolute path

    if not os.path.exists(ppt_path):
        print(f"Error: PowerPoint file '{ppt_path}' not found!")
        return False

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("Opening PowerPoint file:", ppt_path)

    powerpoint = win32com.client.Dispatch("PowerPoint.Application")
    powerpoint.Visible = True  # Make sure PowerPoint window is visible

    try:
        presentation = powerpoint.Presentations.Open(ppt_path)
    except Exception as e:
        print(f"Error opening presentation: {e}")
        powerpoint.Quit()
        return False

    try:
        presentation.SaveCopyAs(os.path.join(output_dir), 17)  # Save in output_dir directly
        print(f"Slides exported to {output_dir}")
    except Exception as e:
        print(f"Error exporting slides: {e}")
    finally:
        presentation.Close()
        powerpoint.Quit()

    return True


# Step 2: Create individual video for each slide using MoviePy from images and audio
def create_videos_for_each_slide(output_dir, config_file):
    output_dir = os.path.abspath(output_dir)  # Convert to absolute path
    config_file = os.path.abspath(config_file)  # Convert to absolute path

    if not os.path.exists(config_file):
        print(f"Error: Configuration file '{config_file}' not found!")
        return

    with open(config_file, 'r') as f:
        config = json.load(f)

    # Process each slide and generate video
    for entry in config:
        slide_num = entry.get("slide")
        mp3_path = entry.get("mp3_path")
        mp4_path = entry.get("mp4_path")

        image_file = os.path.join(output_dir, f"Slide{slide_num}.jpg")

        if not os.path.exists(image_file):
            print(f"Error: Image for slide {slide_num} not found at {image_file}")
            continue

        if not os.path.exists(mp3_path):
            print(f"Error: MP3 file for slide {slide_num} not found at {mp3_path}")
            continue

        audio = MP3(mp3_path)
        duration = audio.info.length

        # Create ImageClip with the correct duration and audio
        image_clip = ImageClip(image_file, duration=duration)
        audio_clip = AudioFileClip(mp3_path).subclip(0, duration)

        image_clip = image_clip.set_audio(audio_clip)

        # Write the final video to the specified mp4 path
        image_clip.write_videofile(mp4_path, fps=24)
        print(f"Video for slide {slide_num} created successfully at {mp4_path}")


if __name__ == "__main__":
    ppt_path = "./source-ppt/JesusChrist_BestSongs_Vol1.pptx"  # Path to your PPTX file
    output_dir = "./slide_images"  # Folder to save exported slide images
    config_file = "03_slide-song-mapping.json"  # Config file with slide to song mapping

    # Run the conversion steps
    if ppt_to_images(ppt_path, output_dir):  # Convert PPT to images
        create_videos_for_each_slide(output_dir, config_file)  # Create individual videos
