import json
from pydub import AudioSegment

# Function to read the config.json and process the audio
def main():
    # Path to the config.json file
    config_file_path = '01_extract-bits-from-mp3-songs.json'

    # Read the configuration from config.json
    with open(config_file_path, 'r') as f:
        audio_segments_info = json.load(f)

    # Create an empty AudioSegment to concatenate cuts from all songs
    final_audio = AudioSegment.empty()

    # Loop through each song and extract the specified portion with a fade-out effect
    for segment_info in audio_segments_info:
        song = AudioSegment.from_mp3(segment_info["path"])

        # Get the start and end time in milliseconds
        start_time = segment_info["start_time"] * 1000
        end_time = segment_info["end_time"] * 1000

        # Extract the required portion
        extracted_segment = song[start_time:end_time]

        # Calculate fade duration (min between 3 seconds or total segment duration)
        segment_duration = len(extracted_segment)
        fade_duration = min(3000, segment_duration)  # 3 seconds or less if the segment is shorter

        # Apply fade-out effect on the last 5 seconds
        extracted_segment = extracted_segment.fade_out(fade_duration)

        # Append the extracted portion with fade-out to the final audio
        final_audio += extracted_segment

    # Export the final merged audio to a new MP3 file
    output_path = "mp3-songs/YESU_KRISTU_ALBUM-1_INTRO.mp3"
    final_audio.export(output_path, format="mp3")

    print(f"Merged MP3 with fade-out saved to {output_path}")

# Entry point for the script
if __name__ == "__main__":
    main()
