#!/usr/bin/python

import pyaudio
import time

WIDTH = 2               # sample width (1=8bit, 2=16bit, 3=24bit, or 4=32bit)
CHANNELS = 1            # mono
SAMPLE_RATE = 44100     # sample rate (in hz)

p = pyaudio.PyAudio()

# Callback function pyaudio object will use to record/stream audio
def callback(in_data, frame_count, time_info, status):
    return (in_data, pyaudio.paContinue)

stream = p.open(format=p.get_format_from_width(WIDTH),
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        output=True,
        stream_callback=callback)

stream.start_stream()

ds = 0

while (stream.is_active()):
    time.sleep(0.1)
    ds += 1
    print(ds, " ds")

stream.stop_stream()
stream.close()

p.terminate()
