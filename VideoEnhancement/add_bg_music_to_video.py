import warnings
import json
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, concatenate_audioclips

def apply_fade_effects(audio_clip, fade_duration):
    """Apply fade-in and fade-out effects to an audio clip."""
    return audio_clip.audio_fadein(fade_duration).audio_fadeout(fade_duration)

def loop_background_music(background_music, video_duration, fade_duration=3):
    loops = int(video_duration // background_music.duration) + 1
    music_clips = []

    for _ in range(loops):
        faded_clip = apply_fade_effects(background_music, fade_duration)
        music_clips.append(faded_clip)

    looped_music = concatenate_audioclips(music_clips).subclip(0, video_duration)
    return looped_music

def add_background_music(video_file, background_music_file, output_file, music_volume=0.1, fade_duration=5):
    # Load the video and the background music
    video_clip = VideoFileClip(video_file)
    background_music = AudioFileClip(background_music_file).volumex(music_volume)

    # Check if the background music is shorter than the video duration
    if background_music.duration < video_clip.duration:
        background_music = loop_background_music(background_music, video_clip.duration, fade_duration)
    else:
        background_music = apply_fade_effects(background_music.subclip(0, video_clip.duration), fade_duration)

    # Create a CompositeAudioClip that includes both the original audio and the background music
    original_audio = video_clip.audio
    composite_audio = CompositeAudioClip([original_audio, background_music])

    # Set the composite audio as the audio of the video clip
    video_clip = video_clip.set_audio(composite_audio)

    # Write the result to a new video file
    video_clip.write_videofile(output_file, codec="libx264", audio_codec="aac")

    # Close the clips to release resources
    video_clip.close()
    background_music.close()
    composite_audio.close()

if __name__ == "__main__":
    # Suppress specific warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning, module="moviepy")

    # Load the video and audio files
    input_video_file = 'C:/WorkArea/Judges_Chapter_11_MCQ.mp4'  # Replace with the path to your video file
    background_music_file = './bg-music/Interstellar Mood - Nico Staf.mp3'  # Replace with the path to your audio file
    output_video_file = 'C:/WorkArea/Judges_Chapter_11_MCQ_Final.mp4'  # Replace with the desired output path

    print(f'background_music_file = {background_music_file}')

    add_background_music(input_video_file, background_music_file, output_video_file)
