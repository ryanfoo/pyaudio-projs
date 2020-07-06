'''
    File Name: sine.py
    Author: Ryan Foo
    Date created: 06/27/2020
    Python Version: 2.7

    To execute, enter:
        python sine.py 
'''

#!/usr/bin/python

from select import select
import sys
import time

from matplotlib import pyplot as plt    # -> pip install matplotlib
import numpy as np                      # -> pip install numpy
import pyaudio                          # -> pip install pyaudio

# Menu Commands
menu_commands = {
    "q"                     : "Quit Program",
    "s"                     : "Play / Stop Sound",
    "f <frequency>"         : "Change Frequency",
    "a <amplitude"          : "Change Amplitude",
    "+ <optional frequency>": "Increment by optional frequency",
    "- <optional frequency>": "Decrement by optional frequency",
    "o"                     : "Open/close oscilloscope",
}

# Initialize defaults
FRAMES_PER_BUFFER = 1024            # Frames per buffer
SAMPLE_RATE = 44100                 # Sample rate (in hz)
CHANNELS = 2                        # Stereo
FREQ = 440.                         # default 440 hz
AMPLITUDE = 0.5                     # default amplitude 0.5
TWO_PI = 2 * np.pi                  # Full cycle

AUDIO_STREAM_ENABLED = False        # Audio Enabled Flag
PROGRAM_IS_ACTIVE = True            # Non-thread safe active flag
OSCILLOSCOPE_ENABLED = False        # Oscilloscope Flag

# Oscilloscope Plot
PLOT_TIME   = np.zeros(FRAMES_PER_BUFFER)
PLOT_SIGNAL = np.zeros(FRAMES_PER_BUFFER)

# Callback function pyaudio object will use to stream audio
def callback(in_data, frame_count, time_info, status):
    global FRAME_OFFSET, PLOT_SIGNAL, PLOT_TIME
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
    # list[start:end:step] syntax
    out[::2] = data                         # Write left channel
    out[1::2] = data                        # Write right channel
    #TODO: Remove, this is for audio input
    # Convert input data
    #in_data = np.fromstring(in_data, dtype=np.float32)
    #PLOT_SIGNAL = in_data
    # Set plot data
    PLOT_TIME = xs
    PLOT_SIGNAL = data
    # Write to buffer; output buffer expects array of length FRAMES_PER_BUFFER * NUM_CHANNELS * BYTES_PER_CHANNEL
    return (out.astype(np.float32), pyaudio.paContinue)

# Print Menu
def print_menu():
    print('--- Menu ---')
    for key in menu_commands:
        print(key + ": " + menu_commands[key])

# Handle Keyboard I/O
def handle_kb_input(s, audio_stream):
    global PROGRAM_IS_ACTIVE, AUDIO_STREAM_ENABLED, FREQ, OMEGA, AMPLITUDE, OSCILLOSCOPE_ENABLED
    if s[0] == 'q':
        print("Quitting...")
        PROGRAM_IS_ACTIVE = False
    elif s[0] == 's':
        AUDIO_STREAM_ENABLED = not AUDIO_STREAM_ENABLED
        if AUDIO_STREAM_ENABLED:
            print("Playing sound...")
            audio_stream.start_stream()
        else:
            print("Stopping sound...")
            audio_stream.stop_stream()
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
    elif s[0] == 'o':
        OSCILLOSCOPE_ENABLED = not OSCILLOSCOPE_ENABLED
        if OSCILLOSCOPE_ENABLED:
            print("Drawing output data")
            plt.show(block=False)
        else:
            print("Closing plot")
            plt.close()
    else:
        print("Invalid Input: %s" % (s))
        print_menu()

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

    # Disable until we explicitly enable the stream
    stream.stop_stream()

    # Print command menu
    print_menu()

    # Start scope
    fig, ax = plt.subplots()
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    ax.set_xlim(0, FRAMES_PER_BUFFER)
    ax.set_ylim(-1, 1)
    ax.plot(PLOT_TIME, PLOT_SIGNAL) 
    
    # Main while loop
    while PROGRAM_IS_ACTIVE:
        try:
            # Handle keyboard input, timeout 500ms
            #TODO: don't leave as magic number
            rlist, _, _ = select([sys.stdin], [], [], 0.5)
            if rlist:
                s = sys.stdin.readline()
                handle_kb_input(s, stream)

            # Plot / update figure canvas
            if OSCILLOSCOPE_ENABLED:
                ax.set_xlim(PLOT_TIME[0] / float(SAMPLE_RATE), PLOT_TIME[FRAMES_PER_BUFFER-1] / float(SAMPLE_RATE))
                ax.plot(PLOT_TIME / float(SAMPLE_RATE), PLOT_SIGNAL, c='black')
                fig.canvas.draw()
                # Pause for 1ms to let it redraw
                #TODO: don't leave as magic number
                plt.pause(0.001)

        except Exception as e:
            print("Exception: ", e)
            stream.stop_stream()
            stream.close()
            p.terminate()        
            plt.close()
            exit(0)

    # Kill the stream
    stream.stop_stream()
    stream.close()
    p.terminate()
    # Close plot
    plt.close()
