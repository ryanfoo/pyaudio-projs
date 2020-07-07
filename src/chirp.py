'''
    File Name: chirp.py
    Author: Ryan Foo
    Date created: 06/27/2020
    Python Version: 2.7

    This generates a chirp using non-blocking calls. This can probably be done way more easily by
    generating the whole chirp lookup table all at once but I personally wanted to get experience 
    with chirp generation with realtime.

    To execute, enter:
        python chirp.py
    Optional Flags:
        -t <seconds>    : Set chirp duration (float, in seconds)
        -v <amplitude>  : Set volume/amplitude (float)
        -m <mode>       : Set mode of chirp; options: LINEAR, LOG
        -w <file>       : Write wave file
        -d              : Draw signal + frequency plot 
        -S              : Silent Mode; this still allows plot drawing / writing to wav audio
'''

#!/usr/bin/python

import enum
import math
import os
import sys
import time

from matplotlib import pyplot as plt    # -> pip install matplotlib
from scipy.fftpack import fft
import numpy as np                      # -> pip install numpy
import pyaudio                          # -> pip install pyaudio
import struct
import wave

# Enum for modes
class Mode(enum.Enum):
    LINEAR = 0
    LOG = 1

AMPLITUDE = 0.5                     # Amplitude
FRAMES_PER_BUFFER = 2048            # Frames per buffer
SAMPLE_RATE = 44100                 # Sample rate (in hz)
CHANNELS = 2                        # Stereo
TWO_PI = 2 * np.pi                  # Full cycle

CHIRP_F0 = 0.0001                   # Start Frequency (approximate ~0)
CHIRP_F1 = 20000.                   # End Frequency
CHIRP_DURATION_S = 5.               # chirp duration; 5 seconds by default

MODE = Mode.LINEAR                  # Operation mode; linear by default

WAVE_WRITE_ENABLED = False          # File output writing flag

DRAW_ENABLED = False                # Draw plot flag

AUDIO_ENABLED = True

# Callback function pyaudio object will use to stream audio
def callback(in_data, frame_count, time_info, status):
    global FRAME_OFFSET, signal
    # Fill audio data
    if FRAME_OFFSET + frame_count - 1 > CHIRP_NUM_SAMPLES:
        end = CHIRP_NUM_SAMPLES - FRAME_OFFSET
        # Generate frame of sound
        gen = AMPLITUDE * np.sin(OMEGA[FRAME_OFFSET:CHIRP_NUM_SAMPLES])
        # Convert to float
        data = gen.astype(np.float32)
        # Interleave into stereo data
        out = np.zeros(len(data) * CHANNELS)
        if AUDIO_ENABLED == True:
            out[:end*CHANNELS:2] = data             # Write left channel
            out[1:end*CHANNELS:2] = data            # Write right channel
        signal[FRAME_OFFSET:CHIRP_NUM_SAMPLES] = data
        # Chirp complete!
        return (out.astype(np.float32), pyaudio.paComplete)
    else:
        end = FRAME_OFFSET + frame_count
        # Generate frame of sound
        gen = AMPLITUDE * np.sin(OMEGA[FRAME_OFFSET:end])
        # Convert to float
        data = gen.astype(np.float32)
        # Interleave into stereo data
        out = np.zeros(len(data) * CHANNELS)
        if AUDIO_ENABLED == True:
            out[::2] = data                         # Write left channel
            out[1::2] = data                        # Write right channel
        signal[FRAME_OFFSET:end] = data            
    # Increment frame
    FRAME_OFFSET += frame_count
    # Write to buffer
    return (out.astype(np.float32), pyaudio.paContinue)

if __name__ == '__main__':
    # Process Command Line Arguments
    if len(sys.argv) >= 2:
        argc = 1
        while argc < len(sys.argv):
            flag = sys.argv[argc]
            # DEBUG
            #print("Echo command: %s" % (flag))
            if flag == "-t":
                try:
                    val = float(sys.argv[argc+1])
                    if val < 0:
                        print("Expecting duration over 0 seconds. Defaulting to 5")
                    else:
                        CHIRP_DURATION_S = val
                except:
                    print("Expecting integer for chirp duration. Defaulting to 5")
                print("Chirp Duration = %f" % (CHIRP_DURATION_S))
                argc += 2
            elif flag == "-v":
                try:
                    val = float(sys.argv[argc+1])
                    if val > 1.0 or val < -1.0:
                        print("Expecting volume between -1.0 to 1.0. Defaulting to 0.5")
                    else:
                        AMPLITUDE = val
                except:
                    print("Expecting float for volume. Defaulting to 0.5")
                print("Volume = %f" % (AMPLITUDE))
                argc += 2
            elif flag == "-m":
                try:
                    val = sys.argv[argc+1]
                    if val.lower() == "linear":
                        MODE = Mode.LINEAR
                    elif val.lower() == "log" or val.lower() == "logarithmic":
                        MODE = Mode.LOG
                    else:
                        MODE = Mode.LINEAR
                except:
                    print("Defaulting to linear mode")
                    MODE = Mode.LINEAR
                print("Running %s" % (MODE.name))
                argc += 2
            elif flag == "-w":
                try:
                    val = sys.argv[argc+1]
                    WAVE_OUTPUT_FILENAME = val
                except:
                    print("Defaulting output.wav file write")  
                    WAVE_OUTPUT_FILENAME = "chirp_{0}_{1}s.wav".format(MODE.name, CHIRP_DURATION_S)
                print("Writing to %s" % (WAVE_OUTPUT_FILENAME))
                WAVE_WRITE_ENABLED = True
                argc += 2
            elif flag == "-d":
                DRAW_ENABLED = True
                argc += 1
            elif flag == "-S":
                AUDIO_ENABLED = False
                argc += 1
            else:
                argc += 1

    # Define number of steps
    CHIRP_NUM_SAMPLES = CHIRP_DURATION_S * SAMPLE_RATE

    # Calculate phase table
    if MODE == Mode.LOG:
        # Logarithmic Frequency Equation: f(t) = f0 * (k^t), k = (f1 / f0)^(1/T)
        # T = chirp duration, t = step/time
        CHIRP_CONSTANT = math.pow((CHIRP_F1 / CHIRP_F0), (1. / int(CHIRP_NUM_SAMPLES)))
        # DEBUG
        FREQ_TABLE = CHIRP_F0 * np.power(CHIRP_CONSTANT, np.arange(CHIRP_NUM_SAMPLES))
    else:
        # Linear Frequency Equation: f(t) = c*t + f0, c = (f1 - f0) / T
        # T = chirp duration, t = step/time
        CHIRP_CONSTANT = (CHIRP_F1 - CHIRP_F0) / CHIRP_NUM_SAMPLES
        # Generate Frequency Table
        FREQ_TABLE = (CHIRP_CONSTANT * np.arange(CHIRP_NUM_SAMPLES)) + CHIRP_F0 

    # Init a table for phase values. We add one additional step to calculate previous phase value.
    VALS = TWO_PI * FREQ_TABLE / SAMPLE_RATE
    OMEGA = np.zeros(CHIRP_NUM_SAMPLES+1)
    i = 1
    for val in VALS:
        OMEGA[i] = OMEGA[i-1] + val
        i += 1

    # Declare frame offset variable
    FRAME_OFFSET = 0
    # Create PortAudio interface
    p = pyaudio.PyAudio()
    # Wav output
    signal = np.zeros(CHIRP_NUM_SAMPLES)

    # Open PortAudio Stream
    stream = p.open(format=pyaudio.paFloat32,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            frames_per_buffer=FRAMES_PER_BUFFER,
            output=True,
            stream_callback=callback)

    # Start PortAudio Stream
    stream.start_stream()

    print("Starting chirp")
    t = 0

    # Main while loop
    while stream.is_active():
        try:
            # Sleeping to keep the stream active
            time.sleep(0.1)
            t += 0.1
        except:
            stream.stop_stream()
            stream.close()
            p.terminate()
            exit(0)

    t += 0.1

    print("Chirp completed... executed for %f seconds" % (t))

    # Kill the stream
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Write signal to wav output
    if WAVE_WRITE_ENABLED == True:
        print("Writing audio WAV File...")
        # Create directory
        path = os.getcwd() + "/soundfiles"
        try:
            os.mkdir(path)
            print("Making directory " + path)
        except:
            print("Error occurred while making directory")
        # Write wav file
        wf = wave.open(path + "/" + WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(2))
        wf.setframerate(SAMPLE_RATE)
        # Write as 16-bit integer
        for sample in signal:
            wf.writeframes(struct.pack('h', int(sample * 32767)))
            wf.writeframes(struct.pack('h', int(sample * 32767)))
        wf.close()

    # Plot
    if DRAW_ENABLED == True:
        print("Plotting...")
        fig, axs = plt.subplots(nrows=2, ncols=1, figsize=(20,10))
        # Signal Plot
        axs[0].axis([0, CHIRP_NUM_SAMPLES, -1., 1.])
        axs[0].set_title("Time Domain")
        axs[0].set_xlabel("Samples")
        axs[0].set_ylabel("Amplitude")
        axs[0].plot(np.arange(CHIRP_NUM_SAMPLES), signal)
        
        axs[1].set_title("Frequency Spectrum")
        axs[1].set_xlabel("Frequency (Hz)")
        axs[1].set_ylabel("Magnitude")
        yf = fft(signal)
        norm = 2.0 / CHIRP_NUM_SAMPLES * np.abs(yf[:CHIRP_NUM_SAMPLES / 2]) 
        axs[1].axis([CHIRP_F0, CHIRP_F1, 0, np.amax(norm)])
        axs[1].plot(np.linspace(CHIRP_F0, CHIRP_F1, CHIRP_NUM_SAMPLES / 2.), norm)

        plt.show()

        print("Close GUI to exit program!")
