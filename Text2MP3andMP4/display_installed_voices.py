import pyttsx3

# Initialize the pyttsx3 engine
engine = pyttsx3.init()

# Get the list of available voices
voices = engine.getProperty('voices')

# Print the available voices and their ids
for index, voice in enumerate(voices):
    print(f"Voice ID: {index}")
    print(f"Name: {voice.name}")
    print(f"Languages: {voice.languages}")
    print(f"Gender: {voice.gender}")
    print(f"Age: {voice.age}\n")

engine.stop()
