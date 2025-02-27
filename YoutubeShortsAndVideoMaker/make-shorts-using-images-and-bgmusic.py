import os
import json
import time
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import moviepy.editor as mpy
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


class TransitionType(Enum):
    """Available transition types between images"""
    NONE = "none"
    FADE = "fade"
    CROSSFADE = "crossfade"


@dataclass
class ImageConfig:
    """Configuration for a single image in the video"""
    path: str
    duration: float
    transition: TransitionType = TransitionType.NONE
    transition_duration: float = 1.0

    def __post_init__(self):
        if self.duration < 1:
            raise ValueError("Image duration must be at least 1 second")
        if self.transition_duration >= self.duration:
            raise ValueError("Transition duration must be less than image duration")


@dataclass
class VideoConfig:
    """Main video configuration"""
    images: List[ImageConfig]
    background_music_path: str
    output_video_path: str
    video_size: Tuple[int, int]
    background_music_volume: float
    fps: int = 24
    threads: int = 8
    codec: str = 'libx264'
    audio_codec: str = 'aac'
    bitrate: str = '8000k'
    audio_bitrate: str = '192k'
    color_mode: str = 'RGB24'

    def __post_init__(self):
        if self.background_music_volume < 0 or self.background_music_volume > 1:
            raise ValueError("Background music volume must be between 0 and 1")
        if self.fps < 1:
            raise ValueError("FPS must be positive")
        if self.threads < 1:
            raise ValueError("Thread count must be positive")


def load_configuration(config_path_in: str) -> VideoConfig:
    """
    Load and validate configuration from a JSON file.

    Args:
        config_path_in (str): Path to the configuration JSON file.

    Returns:
        VideoConfig: Validated configuration object

    Raises:
        FileNotFoundError: If config file is not found
        json.JSONDecodeError: If config file is invalid JSON
        ValueError: If config values are invalid
    """
    try:
        with open(config_path_in, 'r') as f:
            config_dict = json.load(f)

        # Convert image configs to ImageConfig objects
        image_configs = [
            ImageConfig(
                path=img['path'],
                duration=img['duration'],
                transition=TransitionType(img.get('transition', 'none')),
                transition_duration=img.get('transition_duration', 1.0)
            )
            for img in config_dict['images']
        ]

        # Create and return VideoConfig object
        return VideoConfig(
            images=image_configs,
            background_music_path=config_dict['background_music_path'],
            output_video_path=config_dict['output_video_path'],
            video_size=tuple(config_dict['video_size']),
            background_music_volume=config_dict['background_music_volume'],
            fps=config_dict.get('fps', 24),
            threads=config_dict.get('threads', 8),
            codec=config_dict.get('codec', 'libx264'),
            audio_codec=config_dict.get('audio_codec', 'aac'),
            bitrate=config_dict.get('bitrate', '8000k'),
            audio_bitrate=config_dict.get('audio_bitrate', '192k'),
            color_mode=config_dict.get('color_mode', 'RGB24')
        )

    except FileNotFoundError:
        logging.error(f"Configuration file not found: {config_path_in}")
        raise
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in configuration file: {config_path_in}")
        raise
    except Exception as e:
        logging.error(f"Error in configuration: {str(e)}")
        raise


def setup_logging(log_file: Optional[str] = None):
    """
    Configure logging settings.

    Args:
        log_file (Optional[str]): Path to log file. If None, logs to console only.
    """
    handlers = [
        logging.StreamHandler()
    ]

    # if log_file:
    #     os.makedirs(os.path.dirname(log_file), exist_ok=True)
    #     handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers
    )


def validate_image_paths(config: VideoConfig) -> None:
    """
    Validate that all specified image paths exist and are valid image files.

    Args:
        config (VideoConfig): Video configuration

    Raises:
        FileNotFoundError: If any image file is not found
        ValueError: If any file is not a valid image format
    """
    valid_extensions = {'.jpg', '.jpeg', '.png', '.webp'}

    for img_config in config.images:
        path = Path(img_config.path)
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {path}")

        if path.suffix.lower() not in valid_extensions:
            raise ValueError(f"Invalid image format for file: {path}")

    logging.info(f"Validated {len(config.images)} image paths")


def process_image_clip(img_config: ImageConfig, video_size: Tuple[int, int]) -> mpy.VideoClip:
    """
    Process a single image into a video clip.

    Args:
        img_config (ImageConfig): Image configuration
        video_size (tuple): Target video dimensions (width, height)

    Returns:
        mpy.VideoClip: Processed video clip with transitions
    """
    try:
        img_clip = mpy.ImageClip(img_config.path)

        # Resize maintaining aspect ratio
        img_clip = img_clip.resize(height=video_size[1])

        # Center crop to target width
        img_clip = img_clip.crop(x_center=img_clip.w / 2, width=video_size[0])

        # Set duration
        img_clip = img_clip.set_duration(img_config.duration)

        # Apply transitions if specified
        if img_config.transition != TransitionType.NONE:
            if img_config.transition == TransitionType.FADE:
                img_clip = img_clip.fadein(img_config.transition_duration)
                img_clip = img_clip.fadeout(img_config.transition_duration)
            elif img_config.transition == TransitionType.CROSSFADE:
                # Crossfade will be handled during clip concatenation
                pass

        return img_clip

    except Exception as e:
        logging.error(f"Error processing image {img_config.path}: {str(e)}")
        raise


def create_background_music(config: VideoConfig, video_duration: float) -> mpy.AudioClip:
    """
    Create background music clip with specified volume and duration.

    Args:
        config (VideoConfig): Video configuration
        video_duration (float): Total video duration

    Returns:
        mpy.AudioClip: Processed background music clip
    """
    logging.info(f"Processing background music from {config.background_music_path}")

    try:
        background_music = mpy.AudioFileClip(config.background_music_path)

        # Handle music shorter than video
        if background_music.duration < video_duration:
            logging.warning("Background music is shorter than video. Will loop.")
            background_music = background_music.fx(mpy.vfx.loop, duration=video_duration)

        # Trim or cut music to exact video duration
        background_music = background_music.subclip(0, video_duration)

        # Apply fade effects and volume
        background_music = (background_music
                            .audio_fadein(2)
                            .audio_fadeout(3)
                            .volumex(config.background_music_volume))

        return background_music

    except Exception as e:
        logging.error(f"Error processing background music: {str(e)}")
        raise


def create_video(config: VideoConfig) -> str:
    """
    Main video creation process.

    Args:
        config (VideoConfig): Video configuration

    Returns:
        str: Path to the created video
    """
    start_time = time.time()

    try:
        # Validate images
        validate_image_paths(config)

        # Prepare output directory
        os.makedirs(os.path.dirname(config.output_video_path), exist_ok=True)

        # Process image clips in parallel
        logging.info("Processing image clips")
        with ThreadPoolExecutor(max_workers=config.threads) as executor:
            video_clips = list(executor.map(
                lambda x: process_image_clip(x, config.video_size),
                config.images
            ))

        # Concatenate clips with transitions
        logging.info("Concatenating clips with transitions")
        if any(img.transition == TransitionType.CROSSFADE for img in config.images):
            final_video = mpy.concatenate_videoclips(
                video_clips,
                method="crossfadein",
                crossfadein=1.0
            )
        else:
            final_video = mpy.concatenate_videoclips(
                video_clips,
                method="compose"
            )

        # Add background music
        background_music = create_background_music(config, final_video.duration)
        final_video = final_video.set_audio(background_music)

        # Export final video
        logging.info(f"Exporting video to {config.output_video_path}")
        final_video.write_videofile(
            config.output_video_path,
            fps=config.fps,
            codec=config.codec,
            audio_codec=config.audio_codec,
            bitrate=config.bitrate,
            audio_bitrate=config.audio_bitrate,
            threads=config.threads,
            preset='medium',
            logger=None  # Suppress moviepy's internal logging
        )

        duration = time.time() - start_time
        logging.info(f"Video created successfully. Processing time: {duration:.2f} seconds")

        return config.output_video_path

    except Exception as e:
        logging.error(f"Error creating video: {str(e)}")
        raise


if __name__ == "__main__":
    """
    Main entry point of the script.
    """
    try:
        # Setup logging with file output
        setup_logging("logs/video_creator.log")

        # Load and validate configuration
        config_path = 'config/make-shorts-using-images-and-bgmusic.json'
        config = load_configuration(config_path)

        # Create video
        output_path = create_video(config)
        logging.info(f"Video created at: {output_path}")

    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        raise
