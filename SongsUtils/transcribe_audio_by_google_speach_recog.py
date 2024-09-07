import os
from google.cloud import speech

# Set up the credentials path to your Google Cloud service account JSON key
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path_to_your_service_account_key.json"

def transcribe_audio(audio_file_path):
    client = speech.SpeechClient()

    # Load the audio file into memory
    with open(audio_file_path, "rb") as audio_file:
        content = audio_file.read()

    # Configure the request with appropriate settings for Malayalam
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,  # Set to the sample rate of your audio file
        language_code="ml-IN",    # Malayalam language code
    )

    # Perform the transcription
    response = client.recognize(config=config, audio=audio)

    # Extract and print the transcribed text
    for result in response.results:
        print("Transcription: {}".format(result.alternatives[0].transcript))

    # Save the transcription to a file
    with open("transcription_output.txt", "w", encoding="utf-8") as file:
        for result in response.results:
            file.write(result.alternatives[0].transcript + "\n")

    print("Transcription saved to 'transcription_output.txt'")

# Call the function with your audio file path
transcribe_audio("converted_audio.wav")  # Use WAV or LINEAR16 format for best results
