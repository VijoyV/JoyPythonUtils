from gtts import gTTS
import os
import time
from gtts.tts import gTTSError
from pydub import AudioSegment


def convert_text_to_speech(md_files):
    for md_file, _ in md_files:
        with open(md_file, 'r', encoding='utf-8') as file:
            malayalam_text = file.read()

        output_mp3 = md_file.replace('.txt', '.mp3')
        output_srt = md_file.replace('.txt', '.srt')

        retries = 3
        while retries > 0:
            try:
                # Convert text to speech and save as MP3
                tts = gTTS(text=malayalam_text, lang='ml')
                tts.save(output_mp3)
                print(f"Converted {md_file} to {output_mp3}")

                # Generate SRT file
                generate_srt(malayalam_text, output_mp3, output_srt)
                print(f"Generated SRT file {output_srt}")

                # Introduce a delay to avoid rate limiting
                time.sleep(5)  # 5 seconds delay between requests
                break
            except gTTSError as e:
                if "429" in str(e):
                    print(f"Rate limit hit, retrying in 60 seconds...")
                    time.sleep(60)  # Wait 60 seconds before retrying
                    retries -= 1
                else:
                    raise


def generate_srt(text, mp3_file, srt_file):
    lines = text.splitlines()
    audio = AudioSegment.from_mp3(mp3_file)

    # Calculate total characters and adjust timing based on text length
    total_characters = sum(len(line) for line in lines)
    total_duration = len(audio)  # in milliseconds

    char_duration = total_duration / total_characters if total_characters else total_duration

    current_time = 0  # Start time in milliseconds

    # Create SRT content
    with open(srt_file, "w", encoding="utf-8") as srt:
        for i, line in enumerate(lines):
            line_duration = len(line) * char_duration
            start_time = current_time
            end_time = start_time + line_duration

            start_time_str = format_time(start_time / 1000)
            end_time_str = format_time(end_time / 1000)

            srt.write(f"{i + 1}\n")
            srt.write(f"{start_time_str} --> {end_time_str}\n")
            srt.write(f"{line}\n\n")

            current_time += line_duration


def format_time(seconds):
    millis = int(seconds * 1000)
    hours = millis // 3600000
    millis %= 3600000
    minutes = millis // 60000
    millis %= 60000
    seconds = millis // 1000
    millis %= 1000
    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"


if __name__ == "__main__":
    output_dir = "C:\\LogosQuiz_Preparation\\Split_Files"

    # Assuming txt_files were generated from the first script and saved in output_dir
    txt_files = [
        (os.path.join(output_dir, filename), filename.replace(".txt", ""))
        for filename in os.listdir(output_dir)
        if filename.endswith(".txt")
    ]

    # Convert each .txt file to an .mp3 file and generate SRT
    convert_text_to_speech(txt_files)
