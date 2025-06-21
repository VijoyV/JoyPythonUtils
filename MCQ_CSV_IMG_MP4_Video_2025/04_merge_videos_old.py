import os
import json
import subprocess

def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

def run_ffmpeg(args):
    subprocess.run(args, check=True)

def main():
    config = load_config()
    video_dir = os.path.join(config["output_dir"], "videos")
    video_list_file = os.path.join(video_dir, "video.txt")
    output_file = os.path.join(config["output_dir"], "final.mkv")

    if not os.path.exists(video_list_file):
        print("❌ video.txt not found.")
        return

    print(f"🎞️ Merging video segments listed in {video_list_file} → {output_file}")

    # Change working directory to where the videos are
    os.chdir(video_dir)

    run_ffmpeg([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", "video.txt",
        "-c", "copy",
        os.path.relpath(output_file, video_dir)  # make output path relative to cwd
    ])

    print(f"✅ Final video created: {output_file}")


if __name__ == "__main__":
    main()
