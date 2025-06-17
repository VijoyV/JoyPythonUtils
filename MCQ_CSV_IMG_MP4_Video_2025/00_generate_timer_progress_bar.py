import json
import os
import numpy as np
import matplotlib.pyplot as plt
from moviepy.editor import VideoClip, AudioFileClip, CompositeAudioClip
import moviepy.audio.fx.all as afx
from matplotlib.font_manager import FontProperties  # For custom fonts
# Function to generate a video frame
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas  # Add this import

# Load configuration from config.json
with open('config_pg_bar.json', 'r') as config_file:
    config = json.load(config_file)

TIMER_DURATION = config["timer_progress_bar"]["TIMER_DURATION"]
VIDEO_SIZE = config["timer_progress_bar"]["VIDEO_SIZE"]
BACKGROUND_COLOR = config["timer_progress_bar"]["BACKGROUND_COLOR"]
FOREGROUND_COLOR = config["timer_progress_bar"]["FOREGROUND_COLOR"]
DIGIT_COLOR = config["timer_progress_bar"]["DIGIT_COLOR"]
DIGIT_FONT_SIZE = config["timer_progress_bar"]["DIGIT_FONT_SIZE"]
DIGIT_FONT_TYPE = config["timer_progress_bar"]["DIGIT_FONT_TYPE"]
BACKGROUND_MUSIC = config["timer_progress_bar"]["BACKGROUND_MUSIC"]
FPS = config["timer_progress_bar"]["FPS"]

DPI = 300
MUSIC_VOLUME = config["timer_progress_bar"]["MUSIC_VOLUME"]
FADEOUT_DURATION = 3


def make_frame(t):
    progress = t / TIMER_DURATION

    fig = plt.figure(figsize=(VIDEO_SIZE / DPI, VIDEO_SIZE / DPI / 12), dpi=DPI)
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.barh(0.5, 1, height=0.9, color=BACKGROUND_COLOR, align='center')
    ax.barh(0.5, progress, height=0.9, color=FOREGROUND_COLOR, align='center')

    font_properties = FontProperties(family=DIGIT_FONT_TYPE, size=DIGIT_FONT_SIZE * (VIDEO_SIZE / 800))
    time_left = max(0, TIMER_DURATION - t)
    ax.text(0.5, 0.4, f"{int(time_left)}", ha='center', va='center', color=DIGIT_COLOR, fontproperties=font_properties)

    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    canvas.draw()

    # 🔧 Get renderer and reshape the RGBA buffer correctly
    renderer = canvas.get_renderer()
    width, height = canvas.get_width_height()
    buf = np.frombuffer(renderer.buffer_rgba(), dtype='uint8')
    img = buf.reshape((height, width, 4))[:, :, :3]  # Drop alpha channel

    plt.close(fig)
    return img

# Create video clip
animation = VideoClip(make_frame, duration=TIMER_DURATION)

# Load background audio if available
if BACKGROUND_MUSIC and os.path.exists(BACKGROUND_MUSIC):
    audio = AudioFileClip(BACKGROUND_MUSIC).subclip(0, TIMER_DURATION).volumex(MUSIC_VOLUME)
    audio = audio.fx(afx.audio_fadeout, FADEOUT_DURATION)
    animation = animation.set_audio(audio)
else:
    print("⚠️ No valid background music file found. Proceeding without audio.")

# Ensure output directory exists
output_path = "output/videos"
os.makedirs(output_path, exist_ok=True)

# Save as MKV
output_filename = os.path.join(output_path, "progress_bar.mkv")
animation.write_videofile(
    output_filename,
    fps=FPS,
    codec="libx264",        # mkv-compatible codec
    audio_codec="aac",      # or "libvorbis" for higher quality in mkv
    bitrate="5000k"
)

print(f"✅ Timer video saved as {output_filename}")
