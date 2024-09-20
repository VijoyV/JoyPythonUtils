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
input_video = "./Throwing Two Dice With Music.mp4"
output_video = "./Throwing Two Dice - Music Faster.mp4"
speed_decrease = 20  # Decrease speed by 15%

change_video_speed(input_video, output_video, speed_decrease, increase=True)
