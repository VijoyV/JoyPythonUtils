import os
from pydub import AudioSegment


def change_speed_mp3(input_file, output_file, speed=1.25):
    # Load the mp3 file
    song = AudioSegment.from_file(input_file)

    # Change the speed by altering the frame rate
    song_with_altered_speed = song._spawn(song.raw_data, overrides={
        "frame_rate": int(song.frame_rate * speed)
    }).set_frame_rate(song.frame_rate)

    # Export the new mp3 file
    song_with_altered_speed.export(output_file, format="mp3")
    print(f"Saved new track: {output_file}")


if __name__ == "__main__":
    directory = "C:\\Users\\vijoy\Music"  # Replace with your directory path

    # Example usage:
    input_file = directory + "\\vJapamala.mp3"  # Can be either MP3 or WAV
    output_file = directory + "\\vJapamala110.mp3"

    # Convert the file to 1.25x speed
    change_speed_mp3(input_file, output_file, speed=1.10)



