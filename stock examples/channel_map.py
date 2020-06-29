#!/usr/bin/python

import pyaudio
import wave
import sys

CHUNK = 1024

if len(sys.argv) < 2:
    print("Plays a wave file.\n\nUsage: $s filename.wav" % sys.argv[0])
    sys.exit(-1)

wf = wave.open(sys.argv[1], 'rb')

p = pyaudio.PyAudio()

"""
Standard L-R stereo
channel_map = (0,1)

Reverse R-L stereo
channel_map = (1,0)

no audio
channel_map = (-1,-1)

left channel only
channel_map = (0, -1)

right channel only
channel_map (-1, 1)

left channel -> right speaker
channel_map = (-1, 0)

right channel -> left speaker
channel_map = (1, -1)
"""

channel_map = (1, -1)

try:
    stream_info = pyaudio.PaMacCoreStreamInfo(
            flags=pyaudio.PaMacCoreStreamInfo.paMacCorePlayNice, # default
            channel_map=channel_map)
except AttributeError:
    print("Sorry, couldn't find PaMacCoreStreamInfo. Make sure that "
            "you're running on Mac OS X.")
    sys.exit(-1)

print("Stream Info Flags:", stream_info.get_flags())
print("Stream Info Channel Map:", stream_info.get_channel_map())

# open stream
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
        channels=wf.getnchannels(),
        rate=wf.getframerate(),
        output=True,
        output_host_api_specific_stream_info=stream_info)

# read data
data = wf.readframes(CHUNK)

# play stream
while data != '':
    stream.write(data)
    data = wf.readframes(CHUNK)

stream.stop_stream()
stream.close()

p.terminate()
