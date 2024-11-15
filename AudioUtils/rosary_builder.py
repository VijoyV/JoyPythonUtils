import os
from pydub import AudioSegment

def trim_audio(audio, start_trim=0, end_trim=0):
    """Trim the specified number of milliseconds from the start and end of the audio."""
    duration = len(audio)
    print(f'Duration of audio is {duration} ms!')
    trimmed_audio = audio[start_trim:duration-end_trim]
    return trimmed_audio

def apply_fade(audio, fade_duration=1000):
    """Apply fade-out to the audio for the last fade_duration milliseconds."""
    return audio.fade_out(fade_duration)

def save_trimmed_faded_audio(audio, file_path):
    """Save the trimmed and faded audio to a new file."""
    file_name, file_extension = os.path.splitext(file_path)
    cleaned_file_path = f"{file_name}_cleaned{file_extension}"
    audio.export(cleaned_file_path, format="mp3")
    print(f"Saved trimmed and faded file: {cleaned_file_path}")
    return cleaned_file_path

def concatenate_files_with_fade(file1, file2, file3, output_file):
    # Load the three mp3 files
    audio1 = AudioSegment.from_file(file1)
    audio2 = AudioSegment.from_file(file2)
    audio3 = AudioSegment.from_file(file3)

    # Trim the specified duration from the start and end of each file
    audio1 = trim_audio(audio1, 100, 500)
    audio2 = trim_audio(audio2, 500, 100)
    audio3 = trim_audio(audio3, 100, 200)

    # Apply fade-out to each file
    audio1 = apply_fade(audio1, 500)  # 500 ms fade out
    audio2 = apply_fade(audio2, 300)  # 300 ms fade out
    audio3 = apply_fade(audio3, 300)  # 300 ms fade out

    # Save the cleaned versions of each file
    cleaned_file1 = save_trimmed_faded_audio(audio1, file1)
    cleaned_file2 = save_trimmed_faded_audio(audio2, file2)
    cleaned_file3 = save_trimmed_faded_audio(audio3, file3)

    # Concatenate the cleaned audio files
    final_audio = (audio1 + audio2 * 3 + audio3
                   + audio1 + audio2 * 10 + audio3
                   + audio1 + audio2 * 10 + audio3
                   + audio1 + audio2 * 10 + audio3
                   + audio1 + audio2 * 10 + audio3
                   + audio1 + audio2 * 10 + audio3)

    # Export the final concatenated file
    final_audio.export(output_file, format="mp3")
    print(f"Saved final concatenated file: {output_file}")

if __name__ == "__main__":
    file1 = "./Base-Japamala/Swargasthanaya.mp3"  # Replace with the path to your file1.mp3
    file2 = "./Base-Japamala/NanmaNiranjaMariyame.mp3"  # Replace with the path to your file2.mp3
    file3 = "./Base-Japamala/Sthuthi.mp3"  # Replace with the path to your file3.mp3
    output_file = "vJapamala.mp3"  # Desired output file name

    # Concatenate and save the final file with fade-outs
    concatenate_files_with_fade(file1, file2, file3, output_file)
