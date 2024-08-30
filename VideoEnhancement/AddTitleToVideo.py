from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np


def create_text_image(text, font_size, color, image_size, bg_color):
    # Create a new image with the specified background color
    image = Image.new('RGB', image_size, bg_color)
    draw = ImageDraw.Draw(image)
    # Use a truetype font
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        print("Font file not found. Please ensure 'arial.ttf' is accessible.")
        return None
    # Calculate text size and position
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_position = ((image_size[0] - text_width) // 2, (image_size[1] - text_height) // 2)
    # Draw the text on the image
    draw.text(text_position, text, font=font, fill=color)
    return image


def add_title_to_video(input_file, output_file, title_text, duration=5):
    # Load the video file
    video = VideoFileClip(input_file)

    # Duration of the video
    video_duration = video.duration

    # Create a text image for the title
    text_image = create_text_image(title_text, font_size=70, color='white', image_size=video.size, bg_color='black')

    if text_image is None:
        print("Failed to create text image.")
        return

    # Convert the text image to a NumPy array
    text_image_np = np.array(text_image)

    # Convert the text image to a VideoClip
    title_clip = ImageClip(text_image_np).set_duration(duration).set_opacity(0.75)

    # Define positions for the title display
    title_start = title_clip.set_start(0).crossfadein(1)
    title_mid = title_clip.set_start(video_duration / 2 - duration / 2).crossfadein(1)
    title_end = title_clip.set_start(video_duration - duration).crossfadein(1)

    # Combine the title clips and the video
    video_with_titles = CompositeVideoClip([video, title_start, title_mid, title_end])

    # Write the result to a file
    video_with_titles.write_videofile(output_file, codec="libx264")


if __name__ == "__main__":
    # Example usage
    input_video     = "C:\\Users\\vijoy\\Downloads\\JoannaArangetramVideo\\Dances\\Dance-01.mp4"
    output_video    = "C:\\Users\\vijoy\\Downloads\\JoannaArangetramVideo\\Dances\\Dance-01-Thodayamangalam.mp4"
    title_text      = "Pavithra, Arini & Joanna - Dance: Thodayamangalam"
    title_duration  = 10  # Title duration in seconds

    add_title_to_video(input_video, output_video, title_text, title_duration)
