import json
import os
import subprocess
import wave
import contextlib
import shutil


def run(cmd):
    print("🔧 Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def get_audio_duration(path):
    with contextlib.closing(wave.open(path, 'r')) as f:
        return f.getnframes() / float(f.getframerate())


def make_slide_video(image, audio, out_video, fade_duration):
    duration = get_audio_duration(audio)
    fade_filter = (
        f"fade=t=in:st=0:d={fade_duration},"
        f"fade=t=out:st={duration - fade_duration}:d={fade_duration}"
    )
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image,
        "-i", audio,
        "-t", str(duration),
        "-vf", fade_filter,
        "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        out_video
    ]
    run(cmd)
    return duration


def crossfade_videos(input_files, output, crossfade_duration):
    filter_complex = ""
    inputs = []
    filter_streams = []

    for idx, f in enumerate(input_files):
        inputs += ["-i", f]

    for i in range(len(input_files)):
        filter_streams.append(f"[{i}:v]format=yuv420p[v{i}];")
        filter_streams.append(f"[{i}:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[a{i}];")

    filter_complex += "".join(filter_streams)

    current_video = "[v0]"
    current_audio = "[a0]"
    for i in range(1, len(input_files)):
        next_video = f"[v{i}]"
        next_audio = f"[a{i}]"
        out_video = f"[vxf{i}]"
        out_audio = f"[axf{i}]"
        filter_complex += (
            f"{current_video}{next_video}"
            f"xfade=transition=fade:duration={crossfade_duration}:offset="
            f"{i * (duration_per_slide - crossfade_duration)}{out_video};"
        )
        filter_complex += (
            f"{current_audio}{next_audio}"
            f"acrossfade=d={crossfade_duration}:c1=tri:c2=tri{out_audio};"
        )
        current_video = out_video
        current_audio = out_audio

    cmd = [
        "ffmpeg", "-y", *inputs,
        "-filter_complex", filter_complex,
        "-map", current_video,
        "-map", current_audio,
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        output
    ]
    run(cmd)


def main():
    with open("04_config.json") as f:
        config = json.load(f)

    fade_duration = config.get("fade_duration", 0.5)
    crossfade_duration = config.get("crossfade_duration", 0.5)
    output_file = config["output"]
    slides = config["slides"]

    os.makedirs("temp_videos", exist_ok=True)
    temp_files = []

    global duration_per_slide
    duration_per_slide = 0

    print("🎞️ Generating individual slide videos...")
    for idx, slide in enumerate(slides, start=1):
        image = slide["image"]
        audio = slide["audio"]
        out_vid = f"temp_videos/slide_{idx}.mp4"
        duration = make_slide_video(image, audio, out_vid, fade_duration)
        duration_per_slide = duration  # assume same duration for all slides
        temp_files.append(out_vid)

    print("🎬 Creating final video with crossfades...")
    crossfade_videos(temp_files, output_file, crossfade_duration)

    print("✅ Final video created:", output_file)
    shutil.rmtree("temp_videos")


if __name__ == "__main__":
    main()
