import moviepy.editor as mpy

# Load the video and audio files
video_path = './5 Mindbowing Riddles.mp4'  # Replace with the path to your video file
audio_path = 'C:\\SocialMediaWorkshop\\Stock_Music\\Interstellar Mood - Nico Staf.mp3'  # Replace with the path to your audio file

# Load the video and audio
video_clip = mpy.VideoFileClip(video_path)
background_music = mpy.AudioFileClip(audio_path).subclip(0, video_clip.duration)

# Reduce the volume by 50% (adjust the factor as needed)
background_music = background_music.volumex(0.2)  # Reduces the volume to 50% of the original

# Apply a fade-out effect to the audio 5 seconds before the end of the video
fade_duration = 5  # Duration of the fade-out effect in seconds
background_music = background_music.audio_fadeout(fade_duration)

# Combine the video with the modified background music
final_video = video_clip.set_audio(background_music)

# Export the final video
output_path = './5 Mindbowing Riddles w Music.mp4'  # Replace with the desired output path
final_video.write_videofile(output_path, fps=30)

print(f"Video with background music and fade-out effect has been created successfully: {output_path}!")
