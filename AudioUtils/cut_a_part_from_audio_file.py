from pydub import AudioSegment
import os

def cut_audio(input_file, output_file, t1, t2):
    # Check if the input file exists
    if not os.path.exists(input_file):
        print(f"Error: The file {input_file} does not exist.")
        return

    try:
        # Load the MP3 file
        audio = AudioSegment.from_mp3(input_file)
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    # Convert times from seconds to milliseconds
    t1_ms = t1 * 1000
    t2_ms = t2 * 1000

    # Extract the segment
    cut_audio = audio[t1_ms:t2_ms]

    # Apply a 2-second fade-out effect
    fade_out_duration = 2 * 1000  # 2 seconds in milliseconds
    cut_audio = cut_audio.fade_out(fade_out_duration)

    # Export the cut segment to a new MP3 file
    try:
        cut_audio.export(output_file, format="mp3")
        print(f"Exported cut audio to {output_file}")
    except Exception as e:
        print(f"Error exporting file: {e}")

# Usage example
input_file = "./My Mother at  Sixty Six Suno - Full.mp3"
output_file = "./My Mother at Sixty Six.mp3"
t1 = 0   # Start time in seconds
t2 = 90  # End time in seconds

cut_audio(input_file, output_file, t1, t2)
