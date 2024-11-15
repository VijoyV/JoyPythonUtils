import speech_recognition as sr
from pydub import AudioSegment

# Convert audio to proper format (16 kHz, mono)
sound = AudioSegment.from_wav("./NITHYA_SOUJANYA_DHAYAKA_KARTHAVE_SREE_YESU_NAATHA.WAV")
sound = sound.set_frame_rate(16000).set_channels(1)
sound.export("./NITHYA_SOUJANYA_DHAYAKA_KARTHAVE_SREE_YESU_NAATHA_CONV.WAV", format="wav")

# Initialize recognizer
recognizer = sr.Recognizer()

# Load the smaller WAV file (first 60 seconds)
audio_file = sr.AudioFile("./NITHYA_SOUJANYA_DHAYAKA_KARTHAVE_SREE_YESU_NAATHA_CONV.WAV")
with audio_file as source:
    audio_data = recognizer.record(source)

# Recognize with Malayalam language
try:
    text = recognizer.recognize_google(audio_data, language="ml-IN")
    print("Transcription: ", text)

    # Write the transcription to a .txt file
    with open("./NITHYA_SOUJANYA_DHAYAKA.txt", "w", encoding="utf-8") as file:
        file.write(text)

    print("Transcription saved to 'transcription_output.txt'")

except sr.UnknownValueError:
    print("Google Speech Recognition could not understand audio")
except sr.RequestError as e:
    print(f"Could not request results from Google Speech Recognition service; {e}")
