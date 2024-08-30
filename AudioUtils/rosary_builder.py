from pydub import AudioSegment

def trim_audio(audio, start_trim=0, end_trim=0):
    """Trim the specified number of milliseconds from the start and end of the audio."""
    duration = len(audio)
    print(f'Duration of audio {audio} is {duration} ms!')
    trimmed_audio = audio[start_trim:duration-end_trim]
    return trimmed_audio

def concatenate_files_with_fade(file1, file2, file3, output_file):
    # Load the three mp3 files
    audio1 = AudioSegment.from_file(file1)
    audio2 = AudioSegment.from_file(file2)
    audio3 = AudioSegment.from_file(file3)

    # Trim the specified duration from the start and end of each file
    audio1 = trim_audio(audio1, 100, 500)
    audio2 = trim_audio(audio2, 500, 100)
    audio3 = trim_audio(audio3, 100, 200)

    # Apply fade-out to the last second of each file
    audio1 = audio1.fade_out(500)  # 1000 ms fade out (1 second)
    audio2 = audio2.fade_out(300)  # 1000 ms fade out (1 second)
    audio3 = audio3.fade_out(300)  # 1000 ms fade out (1 second)

    # Repeat file2.mp3 10 times
    audio2_repeated_03_times = audio2 * 3
    audio2_repeated_10_times = audio2 * 10

    # Concatenate the audio files
    final_audio = (audio1 + audio2_repeated_03_times + audio3
                   + audio1 + audio2_repeated_10_times + audio3
                   + audio1 + audio2_repeated_10_times + audio3
                   + audio1 + audio2_repeated_10_times + audio3
                   + audio1 + audio2_repeated_10_times + audio3
                   + audio1 + audio2_repeated_10_times + audio3)

    # Export the final concatenated file
    final_audio.export(output_file, format="mp3")
    print(f"Saved final file: {output_file}")

if __name__ == "__main__":

    file1 = "C:\\Users\\vijoy\\Music\\Base-Japamala\\Swargasthanaya.mp3"       # Replace with the path to your file1.mp3
    file2 = "C:\\Users\\vijoy\\Music\\Base-Japamala\\NanmaNiranjaMariyame.mp3"       # Replace with the path to your file2.mp3
    file3 = "C:\\Users\\vijoy\\Music\\Base-Japamala\\Sthuthi.mp3"       # Replace with the path to your file3.mp3
    output_file = "vJapamala.mp3"  # Desired output file name

    # Concatenate and save the final file with fade-outs
    concatenate_files_with_fade(file1, file2, file3, output_file)
