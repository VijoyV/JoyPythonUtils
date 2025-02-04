import os
import pyttsx3

def text_to_speech(file_path, voice_id=None, rate=None):
    # Extract the file name without the extension
    file_name = os.path.splitext(os.path.basename(file_path))[0]

    # Read the text file
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    # Initialize the pyttsx3 engine
    engine = pyttsx3.init()

    # Set the voice if provided
    if voice_id is not None:
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[voice_id].id)

    # Set the speech rate if provided
    if rate is not None:
        engine.setProperty('rate', rate)

    # Convert text to speech and save as MP3
    output_file = f"{file_name}.mp3"
    engine.save_to_file(text, output_file)
    engine.runAndWait()
    print(f"MP3 file saved as {output_file}")

# Replace 'example.txt' with the path to your text file
# Choose the voice_id based on the list obtained from the previous snippet
text_to_speech('chapter-01-q-01.txt', voice_id=1, rate=120)
