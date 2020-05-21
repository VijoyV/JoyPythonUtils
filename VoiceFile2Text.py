#!/usr/bin/env python3

import wave

import pyaudio
import speech_recognition as sr

AUDIO_FILE = "./voice-files/predefined-parameterised-recording.wav"

def main() :

    # use the audio file as the audio source
    r = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)  # read the entire audio file


    # recognize speech using Google Speech Recognition
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        print("Google thinks you said '" + r.recognize_google(audio) + "'")
        PlayWavFile()

    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))


def PlayWavFile():
    # define stream chunk
    chunk = 1024

    # open a wav format music
    f = wave.open(AUDIO_FILE, "rb")
    # instantiate PyAudio
    p = pyaudio.PyAudio()

    print("\n<<< Audio File Properties >>>")
    print("format = {0} \nchannels = {1} \nrate = {2}" .format(p.get_format_from_width(f.getsampwidth()), f.getnchannels(), f.getframerate()))

    # open stream
    stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                    channels=f.getnchannels(),
                    rate=f.getframerate(),
                    output=True)
    # read data
    data = f.readframes(chunk)

    # play stream
    while data:
        stream.write(data)
        data = f.readframes(chunk)

        # stop stream
    stream.stop_stream()
    stream.close()

    # close PyAudio
    p.terminate()

if __name__ == '__main__' :
    main()