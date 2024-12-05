import os
import json
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, VideoClip


def wipe_transition(clip1, clip2, duration, direction="left-to-right"):
    """
    Create a custom wipe transition between two clips.
    """
    def make_mask(t):
        """
        Generate a mask frame for time `t` during the transition.
        """
        progress = t / duration
        w, h = clip1.size
        mask = np.zeros((h, w), dtype=np.uint8)

        if direction == "left-to-right":
            mask[:, :int(w * progress)] = 255
        elif direction == "right-to-left":
            mask[:, int(w * (1 - progress)):] = 255
        elif direction == "top-to-bottom":
            mask[:int(h * progress), :] = 255
        elif direction == "bottom-to-top":
            mask[int(h * (1 - progress)):, :] = 255

        return mask

    # Create the mask clip
    mask_clip = VideoClip(lambda t: make_mask(t), duration=duration).set_fps(24)
    mask_clip.ismask = True  # Mark as mask

    # Apply the mask to the second clip
    clip2_with_mask = clip2.set_mask(mask_clip)

    # Composite the two clips
    return CompositeVideoClip([clip1.set_duration(duration), clip2_with_mask])


def create_video_with_images_and_audio(config_file, transition_duration=1, direction="left-to-right"):
    """
    Create a video combining an MP3 song and multiple images with specified timings and transitions.
    """
    # Load configuration
    with open(config_file, 'r') as f:
        config = json.load(f)

    mp3_file = config.get("mp3_file")
    output_video = config.get("output_video")
    image_settings = config.get("images", [])

    # Validate MP3 file
    if not os.path.exists(mp3_file):
        raise FileNotFoundError(f"Error: MP3 file '{mp3_file}' not found.")

    # Validate image files
    for image_setting in image_settings:
        if not os.path.exists(image_setting["image"]):
            raise FileNotFoundError(f"Error: Image file '{image_setting['image']}' not found.")

    print("Creating video...")

    # Create audio clip
    audio_clip = AudioFileClip(mp3_file)
    song_duration = audio_clip.duration

    print(f"MP3 Song Duration: {song_duration} seconds")

    # Create video clips
    video_clips = []
    for i, image_setting in enumerate(image_settings):
        image_path = image_setting["image"]
        start_time = image_setting["start_time"]
        end_time = image_setting["end_time"]

        # Validate times
        if end_time <= start_time:
            raise ValueError(f"Invalid timing for image {image_path}: end_time must be greater than start_time.")

        # Calculate duration for the current clip
        duration = end_time - start_time

        # Create the image clip
        image_clip = ImageClip(image_path, duration=duration)

        # Add to video_clips
        video_clips.append(image_clip)

        # Add transition to the next clip if not the last image
        if i + 1 < len(image_settings):
            next_image_path = image_settings[i + 1]["image"]
            next_image_clip = ImageClip(next_image_path, duration=duration)
            transition_clip = wipe_transition(image_clip, next_image_clip, transition_duration, direction)
            video_clips.append(transition_clip)

    # Concatenate all video clips
    final_video = concatenate_videoclips(video_clips, method="compose").set_audio(audio_clip)

    # Write the final video to a file
    final_video.write_videofile(output_video, fps=24, codec="libx264", audio_codec="aac")
    print(f"Video created successfully: {output_video}")


if __name__ == "__main__":
    config_file = "./04_song_images_mapping.json"
    try:
        create_video_with_images_and_audio(config_file, transition_duration=1, direction="left-to-right")
    except Exception as e:
        print(f"An error occurred: {e}")
