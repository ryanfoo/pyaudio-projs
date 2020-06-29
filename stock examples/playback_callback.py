#!/usr/bin/python

import pyaudio
import wave
import time
import sys

CHUNK = 1024

if len(sys.argv) < 2:
    print("Plays a wave file.\n\nUsage: $s filename.wav" % sys.argv[0])
    sys.exit(-1)

wf = wave.open(sys.argv[1], 'rb')

p = pyaudio.PyAudio()

# Callback function pyaudio object will use to stream audio
def callback(in_data, frame_count, time_info, status):
    data = wf.readframes(frame_count)
    return (data, pyaudio.paContinue)

stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
        channels=wf.getnchannels(),
        rate=wf.getframerate(),
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
