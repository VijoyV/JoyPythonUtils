import os
import json
import win32com.client  # This line was missing, now added.
from mutagen.mp3 import MP3
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips


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

    # Save slides as images directly in the output_dir without creating subdirectory
    try:
        presentation.SaveCopyAs(os.path.join(output_dir), 17)  # Save in output_dir directly
        print(f"Slides exported to {output_dir}")
    except Exception as e:
        print(f"Error exporting slides: {e}")
    finally:
        presentation.Close()
        powerpoint.Quit()

    return True


# Step 2: Create a video using MoviePy from images and audio
def create_video_from_images_and_audio(output_dir, config_file, output_video):
    output_dir = os.path.abspath(output_dir)  # Convert to absolute path
    output_video = os.path.abspath(output_video)  # Convert to absolute path
    config_file = os.path.abspath(config_file)  # Convert to absolute path

    if not os.path.exists(config_file):
        print(f"Error: Configuration file '{config_file}' not found!")
        return

    with open(config_file, 'r') as f:
        config = json.load(f)

    default_duration = config.get('default_duration', 10)
    slides_without_audio = config.get('slides_without_audio', [])
    song_mappings = config.get('songs', {})

    video_clips = []

    # Process slides
    for slide_num in range(1, 8):  # Assuming there are 13 slides (update if necessary)
        image_file = os.path.join(output_dir, f"Slide{slide_num}.jpg")

        if not os.path.exists(image_file):
            print(f"Error: Image for slide {slide_num} not found at {image_file}")
            return

        if slide_num in slides_without_audio:
            # Slide without audio, use default duration
            image_clip = ImageClip(image_file, duration=default_duration)
            video_clips.append(image_clip)
        elif str(slide_num) in song_mappings:
            audio_file = song_mappings[str(slide_num)]
            if os.path.exists(audio_file):
                # Song exists, use song duration
                audio = MP3(audio_file)
                duration = audio.info.length

                # Create an ImageClip with Audio
                image_clip = ImageClip(image_file, duration=duration + 1)
                audio_clip = AudioFileClip(audio_file).subclip(0, duration)
                print(f'image file {image_file} and its audio file {audio_file} found..! audio duration = {duration} seconds')
                image_clip = image_clip.set_audio(audio_clip)

                video_clips.append(image_clip)
            else:
                # Song doesn't exist, use default duration
                print(f"Warning: {audio_file} not found. Using default duration for slide {slide_num}.")
                image_clip = ImageClip(image_file, duration=default_duration)
                video_clips.append(image_clip)
        else:
            # Slide not in song mappings, assume no audio, use default duration
            image_clip = ImageClip(image_file, duration=default_duration)
            video_clips.append(image_clip)

    # Concatenate all the video clips into one final video
    final_video = concatenate_videoclips(video_clips, method="compose")

    # Write the final video to file
    final_video.write_videofile(output_video, fps=24)
    print(f"Video created successfully: {output_video}")


if __name__ == "__main__":
    ppt_path = "./ChristianMarianSongs_Selected_5.pptx"  # Use absolute path to your PPTX file
    output_dir = "./slide_images"  # Folder to save exported slide images
    output_video = "./ChristianMarianSongs_Selected_5.mp4"  # Final output MP4 file
    config_file = "./slide-song-mapping.json"  # Config file with slide to song mapping

    # Run the conversion steps
    if ppt_to_images(ppt_path, output_dir):  # Convert PPT to images
        create_video_from_images_and_audio(output_dir, config_file, output_video)  # Create video
