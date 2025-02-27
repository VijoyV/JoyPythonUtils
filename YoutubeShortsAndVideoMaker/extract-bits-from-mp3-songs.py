import os
import json
import logging
from pydub import AudioSegment
from dataclasses import dataclass
from typing import Optional


@dataclass
class SongConfig:
    path: str
    start_time: float
    end_time: float
    duration: Optional[float] = None

    def __post_init__(self):
        self.duration = self.end_time - self.start_time


def setup_logging(log_level=logging.INFO):
    """Configure logging settings."""
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s: %(message)s',
        handlers=[
            # logging.FileHandler('audio_merger.log'),
            logging.StreamHandler()
        ]
    )


def validate_config(config_data):
    """Validate configuration input."""
    if not isinstance(config_data, dict):
        raise ValueError("Configuration must be a dictionary")

    if "output_path" not in config_data:
        raise KeyError("Missing required key: output_path")

    if "audio_segments" not in config_data:
        raise KeyError("Missing required key: audio_segments")

    if not isinstance(config_data["audio_segments"], list):
        raise ValueError("audio_segments must be a list")

    for segment in config_data["audio_segments"]:
        required_keys = ["path", "start_time", "end_time"]
        for key in required_keys:
            if key not in segment:
                raise KeyError(f"Missing required key in segment: {key}")

        if not os.path.exists(segment["path"]):
            raise FileNotFoundError(f"Audio file not found: {segment['path']}")


def process_audio_segment(segment: SongConfig, fade_duration=2000):
    """
    Process a single audio segment with fade-in and fade-out.

    Args:
        segment (SongConfig): Segment configuration
        fade_duration (int): Fade duration in milliseconds

    Returns:
        AudioSegment: Processed audio segment
    """
    try:
        song = AudioSegment.from_mp3(segment.path)

        # Extract segment
        start_time = int(segment.start_time * 1000)
        end_time = int(segment.end_time * 1000)
        extracted_segment = song[start_time:end_time]

        # Calculate fade duration
        segment_duration = len(extracted_segment)
        actual_fade_duration = min(fade_duration, segment_duration // 2)

        # Apply fade-in and fade-out
        processed_segment = extracted_segment.fade_in(actual_fade_duration).fade_out(actual_fade_duration)

        logging.info(f"Processed segment from {segment.path} (duration: {segment.duration:.2f}s)")
        return processed_segment

    except Exception as e:
        logging.error(f"Error processing segment: {e}")
        raise


def merge_audio_segments(config_file_path):
    """
    Merge audio segments from configuration file.

    Args:
        config_file_path (str): Path to configuration JSON

    Returns:
        str: Path to merged audio file
    """
    setup_logging()

    try:
        # Read configuration
        with open(config_file_path, 'r') as f:
            config_data = json.load(f)

        # Validate configuration
        validate_config(config_data)

        # Convert segments to SongConfig objects
        segments = [
            SongConfig(**segment)
            for segment in config_data["audio_segments"]
        ]

        # Process and merge segments
        final_audio = AudioSegment.empty()
        for segment in segments:
            processed_segment = process_audio_segment(segment)
            final_audio += processed_segment

        # Get output path from config
        output_path = config_data["output_path"]

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Export merged audio
        final_audio.export(output_path, format="mp3")

        logging.info(f"Merged MP3 saved to {output_path}")
        return output_path

    except Exception as e:
        logging.error(f"Error during audio merging: {e}")
        raise


def main():
    """Main entry point for the script."""
    config_file_path = 'config/extract-bits-from-mp3-songs.json'

    try:
        merge_audio_segments(config_file_path)
    except Exception as e:
        logging.error(f"Script execution failed: {e}")


if __name__ == "__main__":
    main()
