import json
import numpy as np
import matplotlib.pyplot as plt
from moviepy.editor import VideoClip, AudioFileClip, CompositeAudioClip
from moviepy.video.io.bindings import mplfig_to_npimage
import moviepy.audio.fx.all as afx
import moviepy.video.fx.all as vfx  # Import the video effects
from matplotlib.font_manager import FontProperties  # For custom fonts

# Load configuration from config.json
with open('config/timer_progress_bar_config.json', 'r') as config_file:
    config = json.load(config_file)

TIMER_DURATION = config["TIMER_DURATION"]
VIDEO_SIZE = config["VIDEO_SIZE"]  # Size in pixels for the square video (e.g., 640 for 640x640)
BACKGROUND_COLOR = config["BACKGROUND_COLOR"]
FOREGROUND_COLOR = config["FOREGROUND_COLOR"]
DIGIT_COLOR = config["DIGIT_COLOR"]
DIGIT_FONT_SIZE = config["DIGIT_FONT_SIZE"]
DIGIT_FONT_TYPE = config["DIGIT_FONT_TYPE"]  # New font type from config
BACKGROUND_MUSIC = config["BACKGROUND_MUSIC"]
FPS = config["FPS"]

# High DPI setting for higher quality graphics
DPI = 300  # Higher DPI for better resolution
MUSIC_VOLUME = config.get("MUSIC_VOLUME", 0.3)  # Default volume level at 30%
FADEOUT_DURATION = 3  # Background music fade out in the last 3 seconds


# Function to create the progress bar animation for the timer
def make_frame(t):
    # Normalize time (0 to 1)
    progress = t / TIMER_DURATION

    # Set up the plot with a wider aspect ratio (fullscreen progress bar)
    fig, ax = plt.subplots(figsize=(VIDEO_SIZE / DPI, VIDEO_SIZE / DPI / 12), dpi=DPI)  # Adjust ratio for horizontal bar
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])  # Remove x-axis labels
    ax.set_yticks([])  # Remove y-axis labels

    # Remove frame lines (spines)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    # Draw the background for the progress bar
    ax.barh(0.5, 1, height=0.9, color=BACKGROUND_COLOR, align='center')  # Full background bar

    # Draw the foreground (progress) bar with configurable progress
    ax.barh(0.5, progress, height=0.9, color=FOREGROUND_COLOR, align='center')  # Foreground progress bar

    # Define the font properties and scale it relative to the frame size
    font_properties = FontProperties(family=DIGIT_FONT_TYPE, size=DIGIT_FONT_SIZE * (VIDEO_SIZE / 800))  # Adjust font size

    # Correct placement of countdown text
    time_left = max(0, TIMER_DURATION - t)  # Ensure time_left is defined before use
    ax.text(0.5, 0.4, f"{int(time_left)}", ha='center', va='center', color=DIGIT_COLOR, fontproperties=font_properties)

    # Adjust layout to remove margins
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # Convert the matplotlib figure to an image frame
    img = mplfig_to_npimage(fig)
    plt.close(fig)  # Close the figure to free up memory
    return img


# Create the video
animation = VideoClip(make_frame, duration=TIMER_DURATION)

# Load the background music and control volume
audio = AudioFileClip(BACKGROUND_MUSIC).subclip(0, TIMER_DURATION).volumex(MUSIC_VOLUME)

# Apply fadeout effect in the last 3 seconds
audio = audio.fx(afx.audio_fadeout, FADEOUT_DURATION)

# Set the audio to the video
animation = animation.set_audio(audio)

# Save the video to a file with the configured FPS
output_filename = "timer_progress_bar_30Sec.mp4"
animation.write_videofile(output_filename, fps=FPS, codec="libx264", bitrate="5000k", audio_codec="aac")

print(f"Timer video with background music and custom font saved as {output_filename}")
