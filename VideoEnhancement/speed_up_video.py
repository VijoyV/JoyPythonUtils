from moviepy.editor import VideoFileClip, vfx


def change_video_speed(input_path, output_path, speed_percentage, increase=True):
    # Load the video
    clip = VideoFileClip(input_path)

    # Calculate the speed factor based on increase or decrease
    if increase:
        speed_factor = 1 + (speed_percentage / 100.0)  # Increase speed
    else:
        speed_factor = 1 - (speed_percentage / 100.0)  # Decrease speed

    if speed_factor <= 0:
        raise ValueError("The speed percentage is too large, resulting in a negative or zero speed factor.")

    # Apply the speed effect
    adjusted_clip = clip.fx(vfx.speedx, speed_factor)

    # Write the result to a new video file
    adjusted_clip.write_videofile(output_path, codec='libx264')


# Example usage
input_video = "./input/JapamalaVideo.mp4"
output_video = "./output/Japamala-120.mp4"
speed_percentage = 20  # increase / decrease %

change_video_speed(input_video, output_video, speed_percentage, increase=True)
