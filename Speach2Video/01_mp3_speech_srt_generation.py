import speech_recognition as sr
from pydub import AudioSegment
import json
import logging
import time
from pysrt import SubRipFile, SubRipItem, SubRipTime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load config
with open('config/config-03.json', 'r') as f:
    config = json.load(f)

input_mp3 = config['input_mp3']
audio_language = config['audio_language']
srt_filename = config.get('srt_filename', input_mp3.replace('.mp3', '.srt'))

# Log start
logging.info("Starting the speech-to-srt process.")
process_start_time = time.time()

# Step 1: Convert MP3 to WAV for compatibility
logging.info("Converting .mp3 to .wav for compatibility...")
audio = AudioSegment.from_mp3(input_mp3)
audio.export("temp_audio.wav", format="wav")
audio_duration = len(audio) / 1000  # Convert duration to seconds
logging.info(f"Audio duration: {audio_duration:.2f} seconds.")

recognizer = sr.Recognizer()

# Step 2: Recognize speech from WAV file using Google Speech Recognition
text = None
with sr.AudioFile('temp_audio.wav') as source:
    audio_data = recognizer.record(source)

    try:
        logging.info("Recognizing speech using Google Speech Recognition...")
        text = recognizer.recognize_google(audio_data, language=audio_language)
        logging.info(f"Speech recognition successful. Extracted text: {text[:100]}...")
    except sr.UnknownValueError:
        logging.error("Google Speech Recognition could not understand audio")
        exit(1)
    except sr.RequestError as e:
        logging.error(f"Could not request results from Google Speech Recognition service; {e}")
        exit(1)

if not text:
    logging.error("No speech was recognized. Exiting.")
    exit(1)

# Step 3: Generate and save the SRT file
logging.info(f"Generating .srt file: {srt_filename}...")

srt_file = SubRipFile()
words = text.split()
chunk_size = 10  # Number of words per subtitle
num_chunks = len(words) // chunk_size
time_per_chunk = audio_duration / (num_chunks + 1)

# Helper function to convert seconds to SubRipTime
def seconds_to_srt_time(seconds):
    milliseconds = int((seconds - int(seconds)) * 1000)
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return SubRipTime(hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)

# Loop through the text in chunks and assign proper timings
for i in range(0, len(words), chunk_size):
    start_time_seconds = i // chunk_size * time_per_chunk
    end_time_seconds = start_time_seconds + time_per_chunk

    if end_time_seconds > audio_duration:
        end_time_seconds = audio_duration

    if i + chunk_size > len(words):
        chunk_size = len(words) - i

    subtitle_start_time = seconds_to_srt_time(start_time_seconds)
    subtitle_end_time = seconds_to_srt_time(end_time_seconds)
    srt_item = SubRipItem(i // chunk_size, subtitle_start_time, subtitle_end_time, ' '.join(words[i:i + chunk_size]))
    srt_file.append(srt_item)

# Save the SRT file
srt_file.save(srt_filename, encoding='utf-8')
logging.info(f".srt file saved to {srt_filename}.")

# Log total time taken
end_time = time.time()
total_time = end_time - process_start_time
logging.info(f"Total time taken: {total_time:.2f} seconds.")
