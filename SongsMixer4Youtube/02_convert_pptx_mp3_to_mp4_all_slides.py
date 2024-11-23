import json
import os
import math
from mutagen.mp3 import MP3
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
import win32com.client  # Required for PowerPoint COM interface

# Step 1: Export PPT slides as images using win32com.client PowerPoint COM interface
def ppt_to_images(ppt_path, output_dir):
    ppt_path = os.path.abspath(ppt_path)
    output_dir = os.path.abspath(output_dir)

    print(f"Starting slide export from PowerPoint: {ppt_path}")
    if not os.path.exists(ppt_path):
        print(f"Error: PowerPoint file '{ppt_path}' not found!")
        return False

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Output directory '{output_dir}' created.")

    print("Opening PowerPoint file:", ppt_path)
    powerpoint = win32com.client.Dispatch("PowerPoint.Application")
    powerpoint.Visible = True

    try:
        presentation = powerpoint.Presentations.Open(ppt_path)
        print("PowerPoint presentation opened successfully.")
    except Exception as e:
        print(f"Error opening presentation: {e}")
        powerpoint.Quit()
        return False

    # Save each slide as a .jpg image in the output_dir
    try:
        for i, slide in enumerate(presentation.Slides):
            image_file = os.path.join(output_dir, f"Slide{i + 1}.jpg")
            slide.Export(image_file, "JPG")
            print(f"Slide {i + 1} exported as {image_file}")
        print(f"All slides exported successfully to {output_dir}")
    except Exception as e:
        print(f"Error exporting slides: {e}")
    finally:
        presentation.Close()
        powerpoint.Quit()
        print("PowerPoint application closed.")

    return True


# Step 2: Create a video using MoviePy from images and audio
def create_video_from_images_and_audio(output_dir, config_file, output_video):
    output_dir = os.path.abspath(output_dir)  # Convert to absolute path
    output_video = os.path.abspath(output_video)  # Convert to absolute path
    config_file = os.path.abspath(config_file)  # Convert to absolute path

    print(f"Loading configuration from: {config_file}")
    if not os.path.exists(config_file):
        print(f"Error: Configuration file '{config_file}' not found!")
        return

    with open(config_file, 'r') as f:
        config = json.load(f)
    print("Configuration loaded successfully.")

    default_duration = config.get('default_duration', 10)
    slides_without_audio = config.get('slides_without_audio', [])
    song_mappings = config.get('songs', {})

    video_clips = []

    print(f"Scanning {output_dir} for slide images.")
    slide_images = [f for f in os.listdir(output_dir) if f.startswith("Slide") and f.endswith(".jpg")]
    num_slides = len(slide_images)
    print(f"Found {num_slides} slide images for processing.")

    for slide_num in range(1, num_slides + 1):  # Adjust loop to actual number of slides
        image_file = os.path.join(output_dir, f"Slide{slide_num}.jpg")
        print(f"Processing slide {slide_num}...")

        if not os.path.exists(image_file):
            print(f"Error: Image for slide {slide_num} not found at {image_file}")
            continue  # Skip to the next slide if image not found

        if slide_num in slides_without_audio:
            print(f"Slide {slide_num} has no audio. Using default duration of {default_duration} seconds.")
            image_clip = ImageClip(image_file, duration=default_duration)
            video_clips.append(image_clip)
        elif str(slide_num) in song_mappings:
            audio_file = song_mappings[str(slide_num)]
            if os.path.exists(audio_file):
                print(f"Audio file {audio_file} found for slide {slide_num}. Retrieving duration...")
                try:
                    audio = MP3(audio_file)
                    duration = math.floor(audio.info.length)  # Round down to nearest second
                    print(f"Audio duration for slide {slide_num}: {duration} seconds.")

                    # Reduce the duration by a small margin to avoid precision issues
                    duration_safe = max(0, duration - 0.1)
                    image_clip = ImageClip(image_file, duration=duration_safe)
                    audio_clip = AudioFileClip(audio_file).subclip(0, duration_safe)
                    image_clip = image_clip.set_audio(audio_clip)

                    print(f"Slide {slide_num} image and audio combined successfully.")
                    video_clips.append(image_clip)
                except Exception as e:
                    print(f"Error processing audio for slide {slide_num}: {e}")
                    image_clip = ImageClip(image_file, duration=default_duration)
                    video_clips.append(image_clip)
            else:
                print(f"Warning: {audio_file} not found. Using default duration for slide {slide_num}.")
                image_clip = ImageClip(image_file, duration=default_duration)
                video_clips.append(image_clip)
        else:
            print(f"No specific audio mapping for slide {slide_num}. Using default duration.")
            image_clip = ImageClip(image_file, duration=default_duration)
            video_clips.append(image_clip)

    if video_clips:
        print("Concatenating video clips into final video...")
        final_video = concatenate_videoclips(video_clips, method="compose")
        print("Writing final video to file...")
        final_video.write_videofile(output_video, fps=24)
        print(f"Video created successfully: {output_video}")
    else:
        print("Error: No video clips were created. Please check the slide images and configuration.")


if __name__ == "__main__":
    ppt_path = "./source-ppt/JesusChrist_BestSongs_Vol2.pptx"  # Use absolute path to your PPTX file
    output_dir = "./slide_images"  # Folder to save exported slide images
    output_video = "./YESU_KRISTU_FILM_SONGS_VOL-2.mp4"  # Final output MP4 file
    config_file = "02_slide-song-mapping.json"  # Config file with slide to song mapping

    print("Starting PowerPoint to video conversion process...")
    if ppt_to_images(ppt_path, output_dir):  # Convert PPT to images
        print("Slide export completed. Proceeding to video creation...")
        create_video_from_images_and_audio(output_dir, config_file, output_video)  # Create video
    else:
        print("Slide export failed. Aborting video creation.")
    print("Process completed.")
