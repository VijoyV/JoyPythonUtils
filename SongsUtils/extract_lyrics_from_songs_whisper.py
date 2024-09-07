import whisper
from pydub import AudioSegment

# (Optional) Convert MP3 to WAV for better quality
sound = AudioSegment.from_mp3("./ETHRAYUM_DHAYAYULLA_MATHAVE.MP3")
sound.export("converted_song.wav", format="wav")

# Load the Whisper model (choose a model size: tiny, base, small, medium, large)
model = whisper.load_model("medium")  # You can change to "large" if you have the resources

# Transcribe the WAV audio file with language specified as Malayalam
result = model.transcribe("converted_song.wav", language="ml")  # "ml" is the language code for Malayalam

# Get the transcription text
transcription_text = result["text"]

# Write the transcription to a .txt file
with open("transcription_output.txt", "w", encoding="utf-8") as file:
    file.write(transcription_text)

print("Transcription saved to 'transcription_output.txt'")
