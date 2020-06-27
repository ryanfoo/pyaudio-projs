'''
    File Name: sine.py
    Author: Ryan Foo
    Date created: 06/27/2020
    Python Version: 2.7

    To execute, enter:
        python sine.py <opt_frequency> <opt_amplitude>
'''

#!/usr/bin/python

import sys
import time

import numpy as np                  # -> pip install numpy
import pyaudio                      # -> pip install pyaudio

menu_commands = {
    "q": "Quit Program",
    "f <frequency>": "Change Frequency",
    "a <amplitude": "Change Amplitude",
    "+ <optional frequency>": "Increment by optional frequency",
    "- <optional frequency>": "Decrement by optional frequency",
}

def print_menu():
    print('--- Menu ---')
    for key in menu_commands:
        print(key + ": " + menu_commands[key])

FRAMES_PER_BUFFER = 1024            # Frames per buffer
SAMPLE_RATE = 44100                 # Sample rate (in hz)
CHANNELS = 2                        # Mono
FREQ = 440.                         # default 440 hz
AMPLITUDE = 0.5                     # default amplitude 0.5
TWO_PI = 2 * np.pi                  # Full cycle

# Process Command Line Arguments
if len(sys.argv) >= 3:
    try:
        FREQ = float(sys.argv[1])
        if FREQ > 20000. or FREQ <= 0.:
            print("Expecting 0-20000 Hz for frequency. Defaulting to 440 Hz")
            FREQ = 440.
    except:
        print("Invalid input frequency")
    print("Input frequency = %f Hz" % (FREQ))

    try:
        AMPLITUDE = float(sys.argv[2])
        if AMPLITUDE > 1.0 or AMPLITUDE < -1.0:
            print("Expecting -1.0 to 1.0 for amplitude. Defaulting to 0.5")
            AMPLITUDE = 0.5
    except:
        print("Invalid input amplitude")
    print("Input amplitude = %f" % (AMPLITUDE))

# Calculate phase: 2 * PI * frequency / sample rate
OMEGA = TWO_PI * FREQ / SAMPLE_RATE
# Declare frame offset variable
FRAME_OFFSET = 0
# Create PortAudio interface
p = pyaudio.PyAudio()

# Callback function pyaudio object will use to stream audio
def callback(in_data, frame_count, time_info, status):
    global FRAME_OFFSET
    # Init table with frame number
    xs = np.arange(FRAME_OFFSET, FRAME_OFFSET + frame_count)
    # Create table of computed phases according to current frame. numpy's sin function wraps the phase properly.
    gen = AMPLITUDE * np.sin(xs * OMEGA)
    # Increment frame offset 
    FRAME_OFFSET += frame_count
    # Cast array as 32-bit float
    data = gen.astype(np.float32)
    # interleave data 
    out = np.zeros(len(data) * CHANNELS)    # This creates an array twice the size
    # list[start:end:step] syntax
    out[::2] = data                         # Write left channel
    out[1::2] = data                        # Write right channel
    # Write to buffer
    return (out.astype(np.float32), pyaudio.paContinue)

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
    # Sleeping to keep the stream active
    time.sleep(0.1)
    # use input() if using Python 3.0
    s = raw_input()                           
    if s[0] == 'q':
        print("Quitting...")
        break
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
        print_menu()

stream.stop_stream()
stream.close()
p.terminate()
