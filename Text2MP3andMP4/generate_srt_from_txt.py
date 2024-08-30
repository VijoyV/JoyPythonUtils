def create_srt_from_txt(text_file_path, srt_file_path, base_time_per_char=0.05, min_duration=2, max_duration=10):
    with open(text_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    with open(srt_file_path, 'w', encoding='utf-8') as srt_file:
        time_offset = 0
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Calculate the duration for the current line
            duration = calculate_duration(line, base_time_per_char, min_duration, max_duration)

            start_time = time_offset
            end_time = time_offset + duration

            # Convert seconds to hh:mm:ss,ms format
            start_time_str = seconds_to_srt_time(start_time)
            end_time_str = seconds_to_srt_time(end_time)

            # Write the SRT entry
            srt_file.write(f"{i + 1}\n")
            srt_file.write(f"{start_time_str} --> {end_time_str}\n")
            srt_file.write(f"{line}\n\n")

            # Update time offset
            time_offset = end_time


def calculate_duration(text, base_time_per_char=0.05, min_duration=2, max_duration=10):
    duration = len(text) * base_time_per_char
    return max(min_duration, min(duration, max_duration))


def seconds_to_srt_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, remainder = divmod(remainder, 60)
    seconds, milliseconds = divmod(remainder, 1)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{int(milliseconds * 1000):03}"


if __name__ == "__main__":
    text_file_path = "C:/LogosQuiz_Preparation/Split_Files/Judges_Chapter_00.txt"
    srt_file_path = "C:/LogosQuiz_Preparation/Split_Files/Judges_Chapter_00.srt"

    create_srt_from_txt(text_file_path, srt_file_path)

    print(f"SRT file created: {srt_file_path}")
