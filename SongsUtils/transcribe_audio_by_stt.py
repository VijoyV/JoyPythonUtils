import speech_recognition as sr
from pydub import AudioSegment

# Convert audio to proper format (16 kHz, mono)
sound = AudioSegment.from_wav("./ETHRAYUM_DHAYAYULLA_MATHAVE.WAV")
sound = sound.set_frame_rate(16000).set_channels(1)
sound.export("./ETHRAYUM_DHAYAYULLA_MATHAVE_CONV.WAV", format="wav")

# Initialize recognizer
recognizer = sr.Recognizer()

# Load the smaller WAV file (first 60 seconds)
audio_file = sr.AudioFile("./ETHRAYUM_DHAYAYULLA_MATHAVE_CONV.WAV")
with audio_file as source:
    audio_data = recognizer.record(source)

# Recognize with Malayalam language
try:
    text = recognizer.recognize_google(audio_data, language="ml-IN")
    print("Transcription: ", text)

    # Write the transcription to a .txt file
    with open("./ETHRAYUM_DHAYAYULLA_MATHAVE.txt", "w", encoding="utf-8") as file:
        file.write(text)

    print("Transcription saved to 'transcription_output.txt'")

except sr.UnknownValueError:
    print("Google Speech Recognition could not understand audio")
except sr.RequestError as e:
    print(f"Could not request results from Google Speech Recognition service; {e}")
