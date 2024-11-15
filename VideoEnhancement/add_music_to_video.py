import moviepy.editor as mpy

# Load the video and audio files
video_path = './input/JapamalaVideo.mp4'  # Replace with the path to your video file
audio_path = './bg-music/Interstellar Mood - Nico Staf.mp3'  # Replace with the path to your audio file

# Load the video and audio
video_clip = mpy.VideoFileClip(video_path)
background_music = mpy.AudioFileClip(audio_path)

# Loop the audio to match the duration of the video
if background_music.duration < video_clip.duration:
    background_music = mpy.concatenate_audioclips([background_music] * (int(video_clip.duration // background_music.duration) + 1))

# Trim the looped background music to exactly match the video's duration
background_music = background_music.subclip(0, video_clip.duration)

# Reduce the volume by 50% (adjust the factor as needed)
background_music = background_music.volumex(0.2)

# Apply a fade-out effect to the audio 5 seconds before the end of the video
fade_duration = 5  # Duration of the fade-out effect in seconds
background_music = background_music.audio_fadeout(fade_duration)

# Combine the video with the modified background music
final_video = video_clip.set_audio(background_music)

# Export the final video
output_path = './output/JapamalaVideoWithMusic.mp4'  # Replace with the desired output path
final_video.write_videofile(output_path, fps=30)

print(f"Video with background music and fade-out effect has been created successfully: {output_path}!")
