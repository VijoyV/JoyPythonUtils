from pydub import AudioSegment


def convert_ogg_to_mp3(input_file, output_file):
    # Load the .ogg file
    audio = AudioSegment.from_ogg(input_file)

    # Export the audio as .mp3
    audio.export(output_file, format="mp3")


# Example usage
input_file = "C:\\Users\\vijoy\\OneDrive\\Documents\\STFU-Updates\\ChristmasCeleberationMessage_Vicar.ogg"  # Path to the input .ogg file
output_file = "C:\\Users\\vijoy\\OneDrive\\Documents\\STFU-Updates\\ChristmasCeleberationMessage_Vicar.m3"  # Path to save the converted .mp3 file

convert_ogg_to_mp3(input_file, output_file)