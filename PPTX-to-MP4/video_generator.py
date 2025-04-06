import os
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

def generate_video_from_slides(slides_dir, audio_dir, output_video_file, fps, resolution, transition_duration):
    """Generates a video from slide images and narration audio files."""
    slide_files = sorted(
        [f for f in os.listdir(slides_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))],
        key=lambda x: int(''.join(filter(str.isdigit, x)) or 0)
    )
    slide_files = [os.path.join(slides_dir, f) for f in slide_files]
    print(f"Found {len(slide_files)} slide images.")

    clips = []
    for idx, slide_path in enumerate(slide_files, start=1):
        audio_path = os.path.join(audio_dir, f"slide_{idx}.wav")
        if not os.path.exists(audio_path):
            print(f"Audio file {audio_path} not found; skipping slide {idx}.")
            continue

        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration

        image_clip = ImageClip(slide_path).set_duration(duration).set_audio(audio_clip)

        # Ensure resolution is a valid tuple before resizing
        if isinstance(resolution, tuple) and len(resolution) == 2:
            image_clip = image_clip.resize(newsize=resolution)
        else:
            raise ValueError(f"Invalid resolution value: {resolution}. Expected a tuple (width, height).")

        if idx > 1:
            image_clip = image_clip.crossfadein(transition_duration)

        clips.append(image_clip)
        print(f"Created video clip for slide {idx} (duration: {duration:.2f} seconds).")

    if clips:
        final_clip = concatenate_videoclips(clips, method="compose", padding=-transition_duration)
        print("Writing final video file...")
        final_clip.write_videofile(output_video_file, fps=fps, codec="libx264", bitrate="3000k")
        print(f"Video generated: {output_video_file}")
    else:
        print("No clips were created. Check if your slide images and audio files are correctly placed.")
