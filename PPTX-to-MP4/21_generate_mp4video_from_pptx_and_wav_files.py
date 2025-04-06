"""
This code might not be required if you are using PPTX VBA Macro (PPTX_Audio_Embedder.bas)
to embed sound and create mp4 video
"""

import os
from config_loader import load_config
from image_extractor import pptx_to_images
from video_generator import generate_video_from_slides

# --- Load Configuration ---
config = load_config("config-azure.json")

pptx_filename = config["pptx"]["input_file"]
slides_dir = config["video"]["slides_dir"]
audio_dir = config["video"]["audio_dir"]
output_video_file = config["video"]["output_video_file"]
fps = config["video"]["fps"]
resolution = config["video"]["resolution"]  # Should be [width, height]

# Ensure resolution is a tuple of two integers
if isinstance(resolution, list) and len(resolution) == 2 and all(isinstance(i, int) for i in resolution):
    resolution = (resolution[0], resolution[1])  # Convert list to tuple
else:
    raise ValueError(f"Invalid resolution format in config file: {resolution}. Expected [width, height] as integers.")

transition_duration = config["video"]["transition_duration"]

# --- Extract Slides as Images ---
pptx_to_images(pptx_filename, slides_dir, width=resolution[0], height=resolution[1])

# --- Generate Video ---
generate_video_from_slides(slides_dir, audio_dir, output_video_file, fps, resolution, transition_duration)

print("Video generation complete!")
