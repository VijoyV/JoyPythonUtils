from pydub import AudioSegment


def cut_audio(input_file, output_file, t1, t2):
    # Load the .OGG file
    audio = AudioSegment.from_ogg(input_file)

    # Convert times from seconds to milliseconds
    t1_ms = t1 * 1000
    t2_ms = t2 * 1000

    # Extract the segment
    cut_audio = audio[t1_ms:t2_ms]

    # Export the cut segment to a new .OGG file
    cut_audio.export(output_file, format="ogg")


# Usage example
input_file = "C:/DEV/Vicar-Mesage-2024-09-06.ogg"  # Path to the input .OGG file
output_file = "C:/DEV/Vicar-Message-2024-09-07.ogg"  # Path to save the cut segment
t1 = 11  # Start time in seconds
t2 = 45  # End time in seconds

cut_audio(input_file, output_file, t1, t2)
