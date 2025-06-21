import json
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.font_manager import FontProperties
from moviepy.editor import VideoClip, AudioFileClip
import moviepy.audio.fx.all as afx

# === Load configuration ===
with open('config_pg_bar.json', 'r') as f:
    config = json.load(f)["timer_progress_bar"]

# === Configuration Variables ===
TIMER_DURATION = config["TIMER_DURATION"]
WIDTH = config["VIDEO_WIDTH"]
HEIGHT = config["VIDEO_HEIGHT"]
BAR_HEIGHT_RATIO = config.get("BAR_HEIGHT_RATIO", 0.9)
BACKGROUND_COLOR = config["BACKGROUND_COLOR"]
FOREGROUND_COLOR = config["FOREGROUND_COLOR"]
DIGIT_COLOR = config["DIGIT_COLOR"]
DIGIT_FONT_SIZE = config["DIGIT_FONT_SIZE"]
DIGIT_FONT_TYPE = config["DIGIT_FONT_TYPE"]
SHOW_SECONDS_ONLY = config.get("SHOW_SECONDS_ONLY", True)
BACKGROUND_MUSIC = config["BACKGROUND_MUSIC"]
MUSIC_VOLUME = config["MUSIC_VOLUME"]
FADEOUT_DURATION = config.get("FADEOUT_DURATION", 3)
FPS = config["FPS"]
OUTPUT_FILE = config["OUTPUT_PATH"]

# === DPI & Video Size in Inches ===
DPI = 300
figsize = (WIDTH / DPI, HEIGHT / DPI)

# === Frame Generator ===
def make_frame(t):
    progress = t / TIMER_DURATION

    # Setup figure with custom face color to match background
    fig = plt.figure(figsize=figsize, dpi=DPI, facecolor=BACKGROUND_COLOR)
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)
    ax.set_facecolor(BACKGROUND_COLOR)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])

    for spine in ax.spines.values():
        spine.set_visible(False)

    bar_height = BAR_HEIGHT_RATIO
    ax.barh(0.5, 1, height=bar_height, color=BACKGROUND_COLOR, align='center')
    ax.barh(0.5, progress, height=bar_height, color=FOREGROUND_COLOR, align='center')

    # font = FontProperties(family=DIGIT_FONT_TYPE, size=DIGIT_FONT_SIZE)
    scaled_font_size = DIGIT_FONT_SIZE * (HEIGHT / 240)  # Adjust denominator for scaling
    font = FontProperties(family=DIGIT_FONT_TYPE, size=scaled_font_size)
    time_left = max(0, TIMER_DURATION - t)


    if SHOW_SECONDS_ONLY:
        time_text = f"{int(time_left)}"
    else:
        mins = int(time_left) // 60
        secs = int(time_left) % 60
        time_text = f"{mins:02d}:{secs:02d}"

    ax.text(0.5, 0.4, time_text, ha='center', va='center', color=DIGIT_COLOR, fontproperties=font)

    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    canvas.draw()
    renderer = canvas.get_renderer()
    width, height = canvas.get_width_height()
    buf = np.frombuffer(renderer.buffer_rgba(), dtype='uint8')
    img = buf.reshape((height, width, 4))[:, :, :3]  # Drop alpha channel

    plt.close(fig)
    return img

# === Generate Animation ===
animation = VideoClip(make_frame, duration=TIMER_DURATION)

# === Add Background Music if exists ===
if BACKGROUND_MUSIC and os.path.exists(BACKGROUND_MUSIC):
    audio = AudioFileClip(BACKGROUND_MUSIC).subclip(0, TIMER_DURATION).volumex(MUSIC_VOLUME)
    audio = audio.fx(afx.audio_fadeout, FADEOUT_DURATION)
    animation = animation.set_audio(audio)
else:
    print("⚠️ No valid background music file found. Proceeding without audio.")

# === Ensure Output Directory Exists ===
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

# === Write to File ===
animation.write_videofile(
    OUTPUT_FILE,
    fps=FPS,
    codec="libx264",
    audio_codec="aac",
    bitrate="5000k"
)

print(f"✅ Timer video saved as {OUTPUT_FILE}")
