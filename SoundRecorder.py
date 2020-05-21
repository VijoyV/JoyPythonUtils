"""
This is the original code copied from the following gist and modiied by me [vijoye@gmail.com]

https://gist.github.com/mabdrabo/8678538

To Check the quality of your recorded file or generally about the metadata of any file use the following site:

https://www.get-metadata.com/

"""

import wave

import pyaudio

""" Audio Parameter Setting

FORMAT = pyaudio.paInt16 means 16 Bit
CHANNELS = 1. Mono 2. Sterio 
RATE = 16000 Means Sample Rate is 16 KHz

"""

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_SECONDS = 3
WAVE_OUTPUT_FILENAME = "./voice-files/predefined-parameterised-recording.wav"

audio = pyaudio.PyAudio()

# start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

print ("recording...")
frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)
print ("finished recording")

# stop Recording
stream.stop_stream()
stream.close()
audio.terminate()

waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
waveFile.setnchannels(CHANNELS)
waveFile.setsampwidth(audio.get_sample_size(FORMAT))
waveFile.setframerate(RATE)
waveFile.writeframes(b''.join(frames))
waveFile.close()
