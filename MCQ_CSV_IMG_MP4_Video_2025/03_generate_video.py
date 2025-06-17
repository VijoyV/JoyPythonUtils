# 03_generate_video.py

import os
import json
import subprocess
import wave
import contextlib
import shutil
from PIL import Image, ImageDraw, ImageFont
import ffmpeg  # pip install ffmpeg-python


def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)


def get_wav_duration(filepath):
    with contextlib.closing(wave.open(filepath, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        return round(frames / float(rate))


def run_ffmpeg(args):
    subprocess.run(args, check=True)


def generate_question_video(slide_img, audio_path, out_video_path, progress_cfg, narration_duration, font_cfg, marker_cfg):
    frames_dir = "temp_frames"
    os.makedirs(frames_dir, exist_ok=True)

    pb_x = progress_cfg["x"]
    pb_y = progress_cfg["y"]
    pb_w = progress_cfg["width"]
    pb_h = progress_cfg["height"]
    progress_video = os.path.abspath(progress_cfg["video_path"])
    fps = 30

    # Save still image without progress bar outline
    still_img_path = os.path.join(frames_dir, "still.png")
    base_img = Image.open(slide_img).convert("RGBA")
    base_img.convert("RGB").save(still_img_path)

    # Narration video
    narration_video = os.path.join(frames_dir, "narration.mkv")
    run_ffmpeg([
        "ffmpeg", "-y",
        "-loop", "1", "-i", still_img_path,
        "-i", audio_path,
        "-t", str(narration_duration), "-r", str(fps),
        "-c:v", "libx264", "-c:a", "aac", "-pix_fmt", "yuv420p",
        "-shortest", narration_video
    ])

    # Progress bar overlay video
    probe = ffmpeg.probe(progress_video)
    progress_duration = float(probe["format"]["duration"])
    overlay_video = os.path.join(frames_dir, "overlay.mkv")
    run_ffmpeg([
        "ffmpeg", "-y",
        "-loop", "1", "-t", str(progress_duration), "-i", still_img_path,
        "-i", progress_video,
        "-filter_complex", f"[1:v]scale={pb_w}:{pb_h}[bar];[0:v][bar]overlay={pb_x}:{pb_y}:format=auto",
        "-pix_fmt", "yuv420p", "-c:v", "libx264", "-c:a", "aac",
        "-shortest", overlay_video
    ])

    # Final 2s still frame (same as still image)
    still2_path = os.path.join(frames_dir, "still2.png")
    base_img.convert("RGB").save(still2_path)
    still2_video = os.path.join(frames_dir, "still2.mkv")
    run_ffmpeg([
        "ffmpeg", "-y",
        "-loop", "1", "-i", still2_path,
        "-t", "2", "-r", str(fps),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        still2_video
    ])

    # Concatenate video segments
    full_video = os.path.join(frames_dir, "full_video.mkv")
    concat_txt = os.path.join(frames_dir, "concat.txt")
    with open(concat_txt, "w") as f:
        f.write(f"file '{os.path.abspath(narration_video)}'\n")
        f.write(f"file '{os.path.abspath(overlay_video)}'\n")
        f.write(f"file '{os.path.abspath(still2_video)}'\n")

    run_ffmpeg([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_txt,
        "-c", "copy", full_video
    ])

    # Final muxing: narration + visuals (no silence extension)
    run_ffmpeg([
        "ffmpeg", "-y",
        "-i", full_video, "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac", "-shortest",
        out_video_path
    ])

    shutil.rmtree(frames_dir, ignore_errors=True)


def generate_answer_video(slide_img, audio_path, out_video_path):
    run_ffmpeg([
        "ffmpeg", "-y",
        "-loop", "1", "-i", slide_img,
        "-i", audio_path,
        "-c:v", "libx264", "-c:a", "aac",
        "-shortest", "-pix_fmt", "yuv420p", out_video_path
    ])


def generate_videos():
    config = load_config()
    image_dir = os.path.join(config["output_dir"], "images")
    audio_dir = os.path.join(config["output_dir"], "audio")
    video_dir = os.path.join(config["output_dir"], "videos")
    os.makedirs(video_dir, exist_ok=True)

    video_list_path = os.path.join(video_dir, "video.txt")

    with open(video_list_path, "w", encoding="utf-8") as vlist:
        pass  # clear existing file

    font_cfg = {"path": config["font_path"]}
    marker_cfg = config.get("progress_bar_marker", {"enabled": False})

    for filename in sorted(os.listdir(image_dir)):
        if filename.endswith("_q.png"):
            base = filename.replace("_q.png", "")
            img_q = os.path.join(image_dir, f"{base}_q.png")
            img_a = os.path.join(image_dir, f"{base}_a.png")
            aud_q = os.path.join(audio_dir, f"{base}_q.wav")
            aud_a = os.path.join(audio_dir, f"{base}_a.wav")
            out_q = os.path.join(video_dir, f"{base}_q.mkv")
            out_a = os.path.join(video_dir, f"{base}_a.mkv")

            print(f"🎬 Generating {base}_q.mkv")
            q_dur = get_wav_duration(aud_q)
            generate_question_video(img_q, aud_q, out_q, config["progress_bar"], q_dur, font_cfg, marker_cfg)

            print(f"🎬 Generating {base}_a.mkv")
            generate_answer_video(img_a, aud_a, out_a)

            # ✅ Append to video.txt in order
            with open(video_list_path, "a", encoding="utf-8") as vlist:
                vlist.write(f"file '{os.path.basename(out_q)}'\n")
                vlist.write(f"file '{os.path.basename(out_a)}'\n")

if __name__ == "__main__":
    generate_videos()
