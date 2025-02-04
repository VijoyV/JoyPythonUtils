import os
import json
import logging
from pydub import AudioSegment


def setup_logging(log_level=logging.INFO):
    """Configure logging settings."""
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler('audio_merger.log'),
            logging.StreamHandler()
        ]
    )


def validate_config(audio_segments_info):
    """Validate configuration input."""
    if not isinstance(audio_segments_info, list):
        raise ValueError("Configuration must be a list of audio segments")

    for segment in audio_segments_info:
        required_keys = ["path", "start_time", "end_time"]
        for key in required_keys:
            if key not in segment:
                raise KeyError(f"Missing required key: {key}")

        if not os.path.exists(segment["path"]):
            raise FileNotFoundError(f"Audio file not found: {segment['path']}")


def process_audio_segment(segment, fade_duration=2000):
    """
    Process a single audio segment with fade-in and fade-out.

    Args:
        segment (dict): Segment configuration
        fade_duration (int): Fade duration in milliseconds

    Returns:
        AudioSegment: Processed audio segment
    """
    try:
        song = AudioSegment.from_mp3(segment["path"])

        # Extract segment
        start_time = int(segment["start_time"] * 1000)
        end_time = int(segment["end_time"] * 1000)
        extracted_segment = song[start_time:end_time]

        # Calculate fade duration
        segment_duration = len(extracted_segment)
        actual_fade_duration = min(fade_duration, segment_duration // 2)

        # Apply fade-in and fade-out
        processed_segment = extracted_segment.fade_in(actual_fade_duration).fade_out(actual_fade_duration)

        logging.info(f"Processed segment from {segment['path']}")
        return processed_segment

    except Exception as e:
        logging.error(f"Error processing segment: {e}")
        raise


def merge_audio_segments(config_file_path, output_path=None):
    """
    Merge audio segments from configuration file.

    Args:
        config_file_path (str): Path to configuration JSON
        output_path (str, optional): Output file path

    Returns:
        str: Path to merged audio file
    """
    # Setup logging
    setup_logging()

    # Read configuration
    try:
        with open(config_file_path, 'r') as f:
            audio_segments_info = json.load(f)

        # Validate configuration
        validate_config(audio_segments_info)

        # Process and merge segments
        final_audio = AudioSegment.empty()
        for segment in audio_segments_info:
            processed_segment = process_audio_segment(segment)
            final_audio += processed_segment

        # Determine output path if not provided
        if not output_path:
            output_path = "./output/merged_audio.mp3"

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
    output_path = "./output/MotherMary_Songs_Vol_01_SHORT.mp3"

    try:
        merge_audio_segments(config_file_path, output_path)
    except Exception as e:
        logging.error(f"Script execution failed: {e}")


if __name__ == "__main__":
    main()