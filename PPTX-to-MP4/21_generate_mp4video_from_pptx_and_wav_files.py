import os
import json
import time
import win32com.client  # Requires pywin32; works only on Windows with MS Office installed
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips


def pptx_to_images(pptx_file, output_dir, image_format="png", width=1920, height=1080):
    """
    Extracts slides from a PPTX file and saves them as images.
    Uses COM automation to control PowerPoint (Windows only).
    """
    print(f"Extracting slides from {pptx_file} into {output_dir} at {width}x{height} resolution...")
    powerpoint = win32com.client.Dispatch("PowerPoint.Application")
    powerpoint.Visible = 1
    presentation = powerpoint.Presentations.Open(os.path.abspath(pptx_file), WithWindow=False)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Export method saves each slide as an image.
    presentation.Export(os.path.abspath(output_dir), image_format, width, height)

    # Wait a moment to ensure files are written.
    time.sleep(2)

    presentation.Close()
    powerpoint.Quit()
    print("Slide extraction complete.")


# --- Load Configuration ---
config_file = "config-azure.json"
with open(config_file, "r") as f:
    config = json.load(f)

# PPTX & extraction configuration
pptx_filename = config["pptx"]["input_file"]
slides_dir = config["video"]["slides_dir"]
video_resolution = config["video"].get("resolution", [1920, 1080])
transition_duration = config["video"].get("transition_duration", 2)  # in seconds

# Video configuration
audio_dir = config["video"]["audio_dir"]
output_video_file = config["video"]["output_video_file"]
fps = config["video"].get("fps", 24)

# --- Extract Slides as Images from PPTX ---
pptx_to_images(pptx_filename, slides_dir, image_format="png", width=video_resolution[0], height=video_resolution[1])

# --- Get Sorted List of Slide Image Files ---
# Assumes slide images are named like "Slide1.png", "Slide2.png", etc.
slide_files = sorted(
    [f for f in os.listdir(slides_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))],
    key=lambda x: int(''.join(filter(str.isdigit, x)) or 0)
)
slide_files = [os.path.join(slides_dir, f) for f in slide_files]
print(f"Found {len(slide_files)} slide images.")

# --- Create a Video Clip for Each Slide with Crossfade Transition ---
clips = []
for idx, slide_path in enumerate(slide_files, start=1):
    # Corresponding audio file (expects naming like slide_1.wav, slide_2.wav, etc.)
    audio_path = os.path.join(audio_dir, f"slide_{idx}.wav")
    if not os.path.exists(audio_path):
        print(f"Audio file {audio_path} not found; skipping slide {idx}.")
        continue

    # Load the audio clip to determine its duration.
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration

    # Create an image clip for the slide with the duration and attach audio.
    image_clip = ImageClip(slide_path).set_duration(duration).set_audio(audio_clip)

    # Resize if a resolution is provided.
    if video_resolution:
        image_clip = image_clip.resize(newsize=tuple(video_resolution))

    # For all slides except the first, add a crossfade-in transition.
    if idx > 1:
        image_clip = image_clip.crossfadein(transition_duration)

    clips.append(image_clip)
    print(f"Created video clip for slide {idx} (duration: {duration:.2f} seconds).")

# --- Concatenate All Slide Clips into One Video with Transition Overlap ---
if clips:
    final_clip = concatenate_videoclips(clips, method="compose", padding=-transition_duration)
    print("Writing final video file...")
    # Use H.264 codec with higher bitrate for better quality.
    final_clip.write_videofile(output_video_file, fps=fps, codec="libx264", bitrate="3000k")
    print(f"Video generated: {output_video_file}")
else:
    print("No clips were created. Check if your slide images and audio files are correctly placed.")

"""

How It Works
Slide Extraction:
The script uses PowerPoint COM automation to export each slide from the PPTX file as a PNG image at the HD resolution defined in the config (e.g. 1920×1080).

Clip Creation with Transitions:
It then loads the sorted slide images and the corresponding narration audio files. Each slide image is turned into an ImageClip with a duration matching its audio. For slides after the first, a 2‑second crossfade (transition) is added using .crossfadein(transition_duration). When concatenating the clips, a negative padding (equal to the transition duration) is used to overlap clips by 2 seconds, creating the desired transformation effect.

High-Quality Video Generation:
The final video is exported using the H.264 codec at 3000k bitrate for enhanced visual quality.

Update your config file as needed and run the script on a Windows machine with MS Office installed. This should produce an HD MP4 video with smooth 2‑second transitions between slides. Let me know if you need any further adjustments!

"""