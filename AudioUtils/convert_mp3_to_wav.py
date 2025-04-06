from pydub import AudioSegment


def convert_mp3_to_wav(input_file, output_file):
    # Load the .mp3 file
    audio = AudioSegment.from_mp3(input_file)

    # Export the audio as .wav
    audio.export(output_file, format="wav")


# Example usage
input_file = "./Keeping Quiet.mp3"  # Path to the input .mp3 file
output_file = "./Keeping Quiet.wav"  # Path to save the converted .wav file

convert_mp3_to_wav(input_file, output_file)
