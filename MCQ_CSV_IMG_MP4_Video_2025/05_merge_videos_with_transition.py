# 05_merge_videos_with_transition.py

import os
import json
from moviepy.editor import VideoFileClip, CompositeVideoClip, concatenate_videoclips

def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

def get_video_list_from_txt(video_txt_path):
    if not os.path.exists(video_txt_path):
        raise FileNotFoundError(f"File not found: {video_txt_path}")

    with open(video_txt_path, "r", encoding="utf-8") as f:
        files = [line.strip() for line in f if line.strip()]

    videos = []
    for file in files:
        full_path = os.path.join("output", "videos", file)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Video file not found: {full_path}")
        videos.append(full_path)

    return videos

def wipe_transition(clip1, clip2, duration=1.0):
    """Creates a horizontal wipe transition between two clips."""
    clip1 = clip1.set_end(clip1.duration + duration)
    clip2 = clip2.set_start(clip1.duration - duration)

    # Create a mask for clip2 that moves from left to right
    def make_frame(t):
        w, h = clip2.size
        mask = (t / duration) * w
        return lambda gf, t_: gf(t_) * (t_ >= 0) * (t_ < duration)

    clip2_masked = clip2.set_mask(clip2.to_mask().with_start(clip1.duration - duration))

    return CompositeVideoClip([clip1, clip2_masked], size=clip1.size).subclip(0, clip1.duration + clip2.duration - duration)

def merge_with_transitions():
    config = load_config()
    wipe_duration = 1.0

    video_paths = []

    start_slide_video_path = "output/beg-end-videos/start_slide.mkv"
    end_slide_video_path = "output/beg-end-videos/end_slide.mkv"
    video_txt_path = os.path.join("output", "videos", "video.txt")

    if os.path.exists(start_slide_video_path):
        video_paths.append(start_slide_video_path)

    video_paths.extend(get_video_list_from_txt(video_txt_path))

    if os.path.exists(end_slide_video_path):
        video_paths.append(end_slide_video_path)

    # Load all clips
    clips = [VideoFileClip(path) for path in video_paths]

    print(f"🧩 Merging {len(clips)} clips into final_output.mkv ...")

    merged_clips = [clips[0]]

    for i in range(1, len(clips)):
        prev_clip = merged_clips[-1]
        curr_clip = clips[i]

        # Detect transition point (_a.mkv → _q.mkv)
        prev_name = os.path.basename(video_paths[i - 1])
        curr_name = os.path.basename(video_paths[i])
        if prev_name.endswith("_a.mkv") and curr_name.endswith("_q.mkv"):
            # Insert a wipe transition
            print(f"🎞️ Wipe transition between {prev_name} → {curr_name}")
            transition_clip = prev_clip.crossfadeout(wipe_duration).set_end(prev_clip.duration)
            next_clip = curr_clip.crossfadein(wipe_duration)
            merged_clips[-1] = transition_clip
            merged_clips.append(next_clip)
        else:
            merged_clips.append(curr_clip)

    final = concatenate_videoclips(merged_clips, method="compose")
    final.write_videofile("final_output.mkv", codec="libx264", audio_codec="aac")

if __name__ == "__main__":
    merge_with_transitions()
