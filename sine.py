'''
    File Name: sine.py
    Author: Ryan Foo
    Date created: 06/27/2020
    Python Version: 2.7

    To execute, enter:
        python sine.py 
'''

#!/usr/bin/python

import sys
import time

import numpy as np                  # -> pip install numpy
import pyaudio                      # -> pip install pyaudio

# Menu Commands
menu_commands = {
    "q"                     : "Quit Program",
    "s"                     : "Play / Stop Sound",
    "f <frequency>"         : "Change Frequency",
    "a <amplitude"          : "Change Amplitude",
    "+ <optional frequency>": "Increment by optional frequency",
    "- <optional frequency>": "Decrement by optional frequency",
}

# Initialize defaults
FRAMES_PER_BUFFER = 1024            # Frames per buffer
SAMPLE_RATE = 44100                 # Sample rate (in hz)
CHANNELS = 2                        # Stereo
FREQ = 440.                         # default 440 hz
AMPLITUDE = 0.5                     # default amplitude 0.5
TWO_PI = 2 * np.pi                  # Full cycle

AUDIO_ENABLED = False               # Audio Enabled Flag

# Callback function pyaudio object will use to stream audio
def callback(in_data, frame_count, time_info, status):
    global FRAME_OFFSET
    # Used to increment phase per frame
    xs = np.arange(FRAME_OFFSET, FRAME_OFFSET + frame_count)
    # Create table of computed phases according to current frame. numpy's sin function wraps the phase properly.
    gen = AMPLITUDE * np.sin(xs * OMEGA)
    # Increment frame offset 
    FRAME_OFFSET += frame_count
    # Cast array as 32-bit float
    data = gen.astype(np.float32)
    # interleave data 
    out = np.zeros(frame_count * CHANNELS)    # This creates an array twice the size
    if AUDIO_ENABLED == True:
        # list[start:end:step] syntax
        out[::2] = data                         # Write left channel
        out[1::2] = data                        # Write right channel
    # Write to buffer
    return (out.astype(np.float32), pyaudio.paContinue)

# Print Menu
def print_menu():
    print('--- Menu ---')
    for key in menu_commands:
        print(key + ": " + menu_commands[key])

if __name__ == "__main__":
    # Calculate phase: 2 * PI * frequency / sample rate
    OMEGA = TWO_PI * FREQ / SAMPLE_RATE
    # Declare frame offset variable
    FRAME_OFFSET = 0
    # Create PortAudio interface
    p = pyaudio.PyAudio()

    # Open PortAudio Stream
    stream = p.open(format=pyaudio.paFloat32,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            frames_per_buffer=FRAMES_PER_BUFFER,
            output=True,
            stream_callback=callback)

    # Start PortAudio Stream
    stream.start_stream()
        
    # Print command menu
    print_menu()

    # Main while loop
    while stream.is_active():
        try:
            # Sleeping to keep the stream active
            time.sleep(0.1)
            # use input() if using Python 3.0
            s = raw_input()                           
            if s[0] == 'q':
                print("Quitting...")
                break
            elif s[0] == 's':
                if AUDIO_ENABLED == True:
                    AUDIO_ENABLED = False
                    print("Stopping sound...")
                else:
                    AUDIO_ENABLED = True
                    print("Playing sound...")
            elif s[0] == 'f':
                try:
                    v = float(s[2:])
                    FREQ = v
                except:
                    print("Not changing frequency")
                print("Frequency=%f Hz" % (FREQ))
                OMEGA = TWO_PI * FREQ / SAMPLE_RATE
            elif s[0] == 'a':
                try:
                    v = float(s[2:])
                    AMPLITUDE = v
                except:
                    print("Not changing amplitude")
                print("Amplitude=%f" % (AMPLITUDE))
            elif s[0] == '+' or s[0] == '=':
                val = 1.
                try:
                    v = float(s[2:])
                    val = v
                except:
                    print("Incrementing by 1")
                FREQ += val
                print("Frequency=%f Hz" % (FREQ))
                OMEGA = TWO_PI * FREQ / SAMPLE_RATE
            elif s[0] == '_' or s[0] == '-':
                val = 1.
                try:
                    v = float(s[2:])
                    val = v
                except:
                    print("Decrementing by 1")
                FREQ -= val
                print("Frequency=%f Hz" % (FREQ))
                OMEGA = TWO_PI * FREQ / SAMPLE_RATE
            else:
                print("Invalid Input: %s" % (s))
                print_menu()
        except:
            stream.stop_stream()
            stream.close()
            p.terminate()        
            exit(0)

    # Kill the stream
    stream.stop_stream()
    stream.close()
    p.terminate()
