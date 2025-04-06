import moviepy.editor as mp
import numpy as np


def add_background_music(video_path, music_path, output_video_path, loop_music=True):
    # Load the video and audio files
    video = mp.VideoFileClip(video_path)
    audio = mp.AudioFileClip(music_path)

    # Calculate the duration difference
    duration_diff = video.duration - audio.duration

    # If the music is shorter than the video, loop it
    if loop_music and duration_diff > 0:
        # Calculate the number of times the audio needs to be repeated to exceed the video duration
        num_loops = int(np.ceil(video.duration / audio.duration))

        # Create a new audio clip by concatenating the original audio with itself
        new_audio = mp.concatenate_audioclips([audio] * num_loops)

        # Trim the new audio to exactly match the video duration
        new_audio = new_audio.subclip(0, video.duration)
    else:
        new_audio = audio.subclip(0, video.duration)

    fade_duration = 3  # Duration of the fade-out effect in seconds
    new_audio = new_audio.audio_fadeout(fade_duration)

    # Set the audio of the video to the new audio
    final_clip = video.set_audio(new_audio)

    # Export the final video
    final_clip.write_videofile(output_video_path, codec="libx264")


if __name__ == "__main__":
    source_video = "./output/Judges_Chapter_03_MCQ_V2.mp4"
    music_path = "./input/hearty.mp3"
    finished_video = "./output/Judges_Chapter_03_MCQ_V3.mp4"

    add_background_music(source_video, music_path, finished_video)
