#!/usr/bin/python

"""
Input -> Output
"""

import pyaudio

CHUNK = 1024                        # 1024 frames / buffer
FORMAT = pyaudio.paInt16            # 16 bit signed bit depth
WIDTH = 2                           
CHANNELS = 1                        # mono
SAMPLE_RATE = 44100                 # sample rate (in hz)
RECORD_SECONDS = 5                  # record length (in seconds)

p = pyaudio.PyAudio()

stream = p.open(format=p.get_format_from_width(WIDTH),
        channels=CHANNELS,
        rate = SAMPLE_RATE,
        input=True,
        output=True,
        frames_per_buffer=CHUNK)

print("* recording")

frames = []

for i in range(0, int(SAMPLE_RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    stream.write(data, CHUNK)

print("* done")

stream.stop_stream()
stream.close()

p.terminate()
