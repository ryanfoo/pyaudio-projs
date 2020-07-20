'''
    File Name: gen_lookup_table.py
    Author: Ryan Foo
    Date created: 06/28/2020
    Python Version: 2.7

    This generates a sine lookup table over a time period.

    To execute, enter:
        python gen_lookup_table.py
    Optional Flags:
        -n <table_size> : Set table size (integer)
        -v <amplitude>  : Set volume/amplitude (float)
        -f <format>     : Set format (8, 16, 24, 32, 32f, 64f)
        -w <file>       : Write c file
        -d              : Draw signal + frequency plot 
'''

#!/usr/bin/python

import enum
import math
import os
import sys

from matplotlib import pyplot as plt    # -> pip install matplotlib
import numpy as np                      # -> pip install numpy

from oscillator import *

# Enum for formats
class Format(enum.Enum):
    SIGNED_8_BIT = 0,
    SIGNED_16_BIT = 1,
    SIGNED_24_BIT = 2,
    SIGNED_32_BIT = 3,
    FLOAT_32_BIT = 4,
    FLOAT_64_BIT = 5

AMPLITUDE = 0.5                         # Amplitude
NUM_CHANNELS = 2                        # Stereo
TWO_PI = 2 * np.pi                      # Full cycle
TABLE_SIZE = 1024                       # Number of samples to generate
LOOKUP_TABLE_FILENAME = "lookup.h"      # Lookup table filename
DRAW_ENABLED = False                    # Draw plot flag
FORMAT = Format.SIGNED_16_BIT           # Bit Format

if __name__ == '__main__':
    # Process Command Line Arguments
    if len(sys.argv) >= 2:
        argc = 1
        while argc < len(sys.argv):
            flag = sys.argv[argc]
            # DEBUG
            #print("Echo command: %s" % (flag))
            if flag == "-n":
                try:
                    val = int(sys.argv[argc+1])
                    if val < 0:
                        print("Expecting tablesize of over 2. Defaulting to 1024")
                    else:
                        TABLE_SIZE = val
                except:
                    print("Expecting integer for tablesize. Defaulting to 1024")
                print("Tablesize = %f" % (TABLE_SIZE))
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
            elif flag == "-f":
                try:
                    val = sys.argv[argc+1]
                except:
                    print("Default 16bit format")
                argc += 2
            elif flag == "-w":
                try:
                    val = sys.argv[argc+1]
                    LOOKUP_TABLE_FILENAME = val
                except:
                    print("Defaulting lookup.txt write")
                    LOOKUP_TABLE_FILENAME = "sine_{0}.h".format(TABLE_SIZE)
                argc += 2
            elif flag == "-d":
                DRAW_ENABLED = True
                argc += 1
            else:
                argc += 1

    #TODO: Change format conversion given the command line argument
    # Generate Signal
    wave = Sine(TABLE_SIZE)
    #TODO: Implement different waveforms to make wavetables
    #wave = Triangle(TABLE_SIZE)
    #wave = Saw(TABLE_SIZE)
    #wave = Pulse(TABLE_SIZE)
    wave.set_frequency(1.)
    lookup_table = wave.process(TABLE_SIZE) * 32767    
    ## Old algorithm
    #xs = np.arange(TABLE_SIZE)
    #lookup_table = (AMPLITUDE * np.sin(TWO_PI * xs / TABLE_SIZE)) * 32767

    # Create directory
    path = os.getcwd() + "/lookup_tables"
    try:
        os.mkdir(path)
        print("Making directory " + path)
    except:
        print("Error occurred while making directory")

    #TODO: Change fmt specifier given the command line argument
    # Write to file
    np.savetxt(path + "/" + LOOKUP_TABLE_FILENAME, 
            lookup_table, 
            fmt='\t%d,',
            newline='\n', 
            header='#ifndef LOOKUP_H\n#define LOOKUP_H\n\nint16_t sine[%d] = {' % TABLE_SIZE, 
            footer='};\n\n#endif', 
            comments='')

    # Plot
    if DRAW_ENABLED == True:
        print("Plotting...")
        fig, wave_plot = plt.subplots(nrows=1, ncols=1, figsize=(20,10))
        # Signal Plot
        wave_plot.axis([0, TABLE_SIZE, -32767, 32767])
        wave_plot.set_title("Lookup Table")
        wave_plot.set_xlabel("Samples")
        wave_plot.set_ylabel("Amplitude")
        wave_plot.plot(np.arange(TABLE_SIZE), lookup_table)
        
        #fig.tight_layout()
        plt.show()

        print("Close GUI to exit program!")
