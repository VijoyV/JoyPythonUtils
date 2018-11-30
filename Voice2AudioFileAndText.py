#!/usr/bin/env python3

import speech_recognition as sr


# obtain audio from the microphone

r = sr.Recognizer()
with sr.Microphone() as source:
    print("Google Speech Recognition: Say something!")
    audio = r.listen(source)

# recognize speech using Google Speech Recognition
try:
    # for testing purposes, we're just using the default API key
    # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
    # instead of `r.recognize_google(audio)`
    print("Google thinks you said '" + r.recognize_google(audio) + "'")

    # write audio to a WAV file
    with open("./voice-files/microphone-results.wav", "wb") as f:
        f.write(audio.get_wav_data())

except sr.UnknownValueError:
    print("Google Speech Recognition could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Google Speech Recognition service; {0}".format(e))



