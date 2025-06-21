# 04a_create_slide_videos.py

import os
import json
from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    CompositeAudioClip
)


def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)


def create_slide_video(image_path, audio_path, duration, output_path, fade_duration=1.0, volume=0.3):
    print(f"\U0001F3AC Creating slide video: {output_path}")
    clip = ImageClip(image_path).set_duration(duration)

    if audio_path and os.path.exists(audio_path):
        audio = AudioFileClip(audio_path).subclip(0, duration).volumex(volume)
        faded_audio = audio.audio_fadein(fade_duration).audio_fadeout(fade_duration)
        clip = clip.set_audio(faded_audio)

    clip.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")


if __name__ == "__main__":
    config = load_config()
    duration = 10
    fade_duration = 2
    bg_volume = config.get("start_end_music_volume", 0.1)

    start_slide_img = config.get("start_slide")
    end_slide_img = config.get("end_slide")
    bg_music = config.get("start_end_background_music")

    if start_slide_img:
        create_slide_video(start_slide_img, bg_music, duration, "output/beg-end-videos/start_slide.mkv", fade_duration,
                           volume=bg_volume)
    if end_slide_img:
        create_slide_video(end_slide_img, bg_music, duration, "output/beg-end-videos/end_slide.mkv", fade_duration,
                           volume=bg_volume)
