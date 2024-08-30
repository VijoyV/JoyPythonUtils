import moviepy.editor as mpy

# Load the video and audio files
video_path = 'C:\\SocialMediaWorkshop\\Human_Desires.mp4'  # Replace with the path to your video file
audio_path = 'C:\\SocialMediaWorkshop\\dawnofchange.mp3'  # Replace with the path to your audio file

# Load the video and audio
video_clip = mpy.VideoFileClip(video_path)
background_music = mpy.AudioFileClip(audio_path).subclip(0, video_clip.duration)

# Apply a fade-out effect to the audio 5 seconds before the end of the video
fade_duration = 5  # Duration of the fade-out effect in seconds
background_music = background_music.audio_fadeout(fade_duration)

# Combine the video with the modified background music
final_video = video_clip.set_audio(background_music)

# Export the final video
output_path = 'C:\\SocialMediaWorkshop\\Human_Desires_V1.mp4'  # Replace with the desired output path
final_video.write_videofile(output_path, fps=24)

print("Video with background music and fade-out effect has been created successfully!")
