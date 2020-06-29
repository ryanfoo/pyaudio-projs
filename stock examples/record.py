#!/usr/bin/python

import pyaudio
import wave

CHUNK = 1024                        # 1024 frames / buffer
FORMAT = pyaudio.paInt16            # 16 bit signed bit depth
CHANNELS = 1                        # mono
SAMPLE_RATE = 44100                 # sample rate (in hz)
RECORD_SECONDS = 5                  # record length (in seconds)
WAVE_OUTPUT_FILENAME = "output.wav" # file output name

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
        channels=CHANNELS,
        rate = SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK)

print("* recording")

frames = []

for i in range(0, int(SAMPLE_RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(SAMPLE_RATE)
wf.writeframes(b''.join(frames))
wf.close()
