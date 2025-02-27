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

    # Export each slide as an image.
    presentation.Export(os.path.abspath(output_dir), image_format, width, height)

    # Wait briefly to ensure files are written.
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
transition_duration = config["video"].get("transition_duration", 2)

# Video configuration
audio_dir = config["video"]["audio_dir"]
output_video_file = config["video"]["output_video_file"]
fps = config["video"].get("fps", 24)
codec = config["video"].get("codec", "libx264")
bitrate = config["video"].get("bitrate", "3000k")
num_threads = config["video"].get("threads", 8)

# --- Extract Slides as Images from PPTX ---
pptx_to_images(pptx_filename, slides_dir, image_format="png", width=video_resolution[0], height=video_resolution[1])

# --- Get Sorted List of Slide Image Files ---
slide_files = sorted(
    [f for f in os.listdir(slides_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))],
    key=lambda x: int(''.join(filter(str.isdigit, x)) or 0)
)
slide_files = [os.path.join(slides_dir, f) for f in slide_files]
print(f"Found {len(slide_files)} slide images.")

# --- Create a Video Clip for Each Slide with Transition ---
clips = []
for idx, slide_path in enumerate(slide_files, start=1):
    # Get the corresponding audio file.
    audio_path = os.path.join(audio_dir, f"slide_{idx}.wav")
    if not os.path.exists(audio_path):
        print(f"Audio file {audio_path} not found; skipping slide {idx}.")
        continue

    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration

    image_clip = ImageClip(slide_path).set_duration(duration).set_audio(audio_clip)

    # If resolution is provided, ensure the clip is resized.
    if video_resolution:
        image_clip = image_clip.resize(newsize=tuple(video_resolution))

    # For slides after the first, add a crossfade-in transition.
    if idx > 1:
        image_clip = image_clip.crossfadein(transition_duration)

    clips.append(image_clip)
    print(f"Created video clip for slide {idx} (duration: {duration:.2f} seconds).")

# --- Concatenate All Clips into One Video ---
if clips:
    final_clip = concatenate_videoclips(clips, method="compose", padding=-transition_duration)
    print("Writing final video file...")
    final_clip.write_videofile(
        output_video_file,
        fps=fps,
        codec=codec,
        bitrate=bitrate,
        threads=num_threads,
        logger=None  # Disable verbose logging
    )
    print(f"Video generated: {output_video_file}")
else:
    print("No clips were created. Check if your slide images and audio files are correctly placed.")

"""

Explanation
Threading:
The threads parameter is set to 8 (or any number you choose) to allow ffmpeg to use multiple threads for encoding.

Codec and Bitrate:
You can switch between libx264 and h264_nvenc (for Nvidia hardware acceleration) by updating the "codec" in your config. The bitrate is set to 3000k for good quality.

Transition Duration:
Each slide (except the first) gets a crossfade-in transition of 2 seconds, and when concatenating, negative padding of 2 seconds is applied to overlap the clips.

Optimizations:
Disabling the logger (logger=None) reduces overhead in MoviePy. Also, if your slide images are already at HD resolution, the resizing step becomes a lightweight operation.

Keep in mind that video encoding (especially for HD content) is inherently time-consuming. However, using multithreading and hardware acceleration (if available) can significantly reduce the processing time. If your machine supports hardware encoding, consider setting "codec": "h264_nvenc" in your config.

Give these changes a try and see if the processing time improves. Let me know if you have any further questions or adjustments!

"""