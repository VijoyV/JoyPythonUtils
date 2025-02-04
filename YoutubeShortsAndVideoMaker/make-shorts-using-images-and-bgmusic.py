import os
import json
import time
import logging
import moviepy.editor as mpy
from concurrent.futures import ThreadPoolExecutor


def load_configuration(config_path_in):
    """
    Load configuration from a JSON file.

    Args:
        config_path (str): Path to the configuration JSON file.

    Returns:
        dict: Configuration settings
    """
    try:
        with open(config_path_in, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Configuration file not found: {config_path_in}")
        raise
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in configuration file: {config_path_in}")
        raise


def setup_logging():
    """
    Configure logging settings.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def ensure_output_directory(directory):
    """
    Create output directory if it doesn't exist.

    Args:
        directory (str): Path to the directory
    """
    os.makedirs(directory, exist_ok=True)
    logging.info(f"Ensuring output directory exists: {directory}")


def get_image_files(image_folder):
    """
    Retrieve sorted list of image files from the specified folder.

    Args:
        image_folder (str): Path to the image folder

    Returns:
        list: Sorted list of image file paths
    """
    image_extensions = ('webp', 'PNG', 'jpg', 'jpeg')
    image_files = sorted([
        os.path.join(image_folder, img)
        for img in os.listdir(image_folder)
        if img.endswith(image_extensions)
    ])
    logging.info(f"Found {len(image_files)} image files in {image_folder}")
    return image_files


def process_image_clip(image_path, duration, video_size):
    img_clip = mpy.ImageClip(image_path)
    img_clip = img_clip.resize(height=video_size[1])  # Resize maintaining aspect ratio
    img_clip = img_clip.crop(x_center=img_clip.w/2, width=video_size[0])
    img_clip = img_clip.set_duration(duration)
    return img_clip

def create_background_music(background_music_path, video_duration, volume):
    """
    Create background music clip with specified volume and duration.

    Args:
        background_music_path (str): Path to background music file
        video_duration (float): Total video duration
        volume (float): Background music volume

    Returns:
        mpy.AudioFileClip: Processed background music clip
    """
    logging.info(f"Processing background music from {background_music_path}")
    logging.info(f"Background music duration to match: {video_duration} seconds")
    logging.info(f"Background music volume set to: {volume}")

    try:
        background_music = mpy.AudioFileClip(background_music_path)

        # Log original music details
        logging.info(f"Original music duration: {background_music.duration} seconds")

        # Handle music shorter than video
        if background_music.duration < video_duration:
            logging.warning("Background music is shorter than video. Will loop or repeat.")
            # Create a looped version of the music to match video duration
            background_music = background_music.fx(mpy.vfx.loop, duration=video_duration)

        # Trim or cut music to exact video duration
        background_music = background_music.subclip(0, video_duration)

        # Apply fade out and volume
        background_music = background_music.audio_fadeout(3).volumex(volume)

        logging.info(f"Final background music duration: {background_music.duration} seconds")
        return background_music

    except Exception as e:
        logging.error(f"Error processing background music: {e}")
        raise


def create_video(config):
    """
    Main video creation process.

    Args:
        config (dict): Configuration settings

    Returns:
        str: Path to the created video
    """
    # Setup and validation
    setup_logging()
    start_time = time.time()

    # Extract configuration
    image_folder = config['image_folder']
    output_video_path = config['output_video_path']
    background_music_path = config['background_music_path']
    durations_per_image = config['durations_per_image']
    video_size = tuple(config['video_size'])
    background_music_volume = config['background_music_volume']

    # Prepare directories and files
    ensure_output_directory(os.path.dirname(output_video_path))
    image_files = get_image_files(image_folder)

    # Validate image and duration counts
    if len(durations_per_image) != len(image_files):
        raise ValueError("The number of image files and durations must match.")

    # Process image clips in parallel
    logging.info("Processing image clips")
    with ThreadPoolExecutor() as executor:
        video_clips = list(executor.map(
            lambda x: process_image_clip(x[0], x[1], video_size),
            zip(image_files, durations_per_image)
        ))

    # Concatenate video clips
    logging.info("Concatenating image clips")
    final_video = mpy.concatenate_videoclips(video_clips, method="compose")

    # Add background music
    logging.info("Adding background music")
    try:
        background_music = create_background_music(
            background_music_path,
            final_video.duration,
            background_music_volume
        )

        # Create composite audio clip
        logging.info("Creating composite audio clip")
        final_audio = mpy.CompositeAudioClip([background_music])

        # Set audio to video
        logging.info("Setting background music to video")
        final_video = final_video.set_audio(final_audio)

    except Exception as e:
        logging.error(f"Failed to add background music: {e}")
        raise

    # Export final video
    logging.info(f"Exporting video to {output_video_path}")
    final_video.write_videofile(output_video_path, fps=24, threads=8)

    # Calculate and log processing time
    end_time = time.time()
    logging.info(f"Video created successfully at {output_video_path}")
    logging.info(f"Total processing time: {end_time - start_time:.2f} seconds")

    return output_video_path


if __name__ == "__main__":
    """
    Main entry point of the script.
    """
    try:
        config_path = 'config/make-shorts-using-images-and-bgmusic.json'
        config = load_configuration(config_path)
        create_video(config)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise