# Generating .srt File from .mp3

## 1. Configuration and Setup:
Load the necessary parameters from a config.json file to process the .mp3 file and generate subtitles.
Key configurations:
input_mp3: The input MP3 file to be processed.
audio_language: The language used for speech recognition (e.g., ml-IN for Malayalam).
srt_filename: The name of the output .srt file (optional, defaults to the MP3 file name).

## 2. Audio Conversion and Speech Recognition:
Convert the .mp3 file to .wav format for compatibility with the speech recognition module.
Perform speech-to-text conversion using Google Speech Recognition API.

## 3. SRT File Generation:
Split the recognized text into chunks (e.g., 10 words per chunk).
Assign start and end times for each chunk based on the audio duration.
Save the subtitle information in .srt format, ensuring proper time synchronization.
