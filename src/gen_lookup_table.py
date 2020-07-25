'''
    File Name: gen_lookup_table.py
    Author: Ryan Foo
    Date created: 06/28/2020
    Python Version: 3.7

    This generates a sine lookup table over a time period.

    To execute, enter:
        python gen_lookup_table.py
    Optional Flags:
        -w <waveform>   : Set waveform 
        -n <table_size> : Set table size (integer)
        -v <amplitude>  : Set volume/amplitude (float)
        -t <format>     : Set format (8, 16, 24, 32, 32f, 64f)
        -w <file>       : Filename
        -d              : Draw signal + frequency plot 
'''

#!/usr/bin/python

import enum
import getopt
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

# Enum for WAVE_TYPEs
class Waveform(enum.Enum):
    SINE = 0,
    TRI = 1,
    RAMP = 2,
    SAW = 3,
    SQR = 4,
    WHITE = 5

ALIAS_SINE  = {"sine", "sin"}
ALIAS_TRI   = {"triangle", "tri"}
ALIAS_RAMP  = {"ramp up", "ramp"}
ALIAS_SAW   = {"ramp down", "sawtooth", "saw"}
ALIAS_SQR   = {"square", "sqr", "pulse"}
ALIAS_WHITE = {"white noise", "white"}

AMPLITUDE = 1.0                         # Amplitude
TABLE_SIZE = 1024                       # Number of samples to generate
LOOKUP_TABLE_FILENAME = "lookup.h"      # Lookup table filename
DRAW_ENABLED = False                    # Draw plot flag
FORMAT = Format.SIGNED_16_BIT           # Bit Format
FORMAT_C_STRING = "int16_t"             # Format type for C
NP_FORMAT = '\t%d,'                     # Format for np write file
WAVE_TYPE = Waveform.SINE               # Sine Wave

if __name__ == '__main__':
    # Get command line args
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hdn:w:t:a:f:")
    except:
        print("gen_lookup_table.py -n <table_size> -w <WAVE_TYPE> -t <format> -a <amplitude> -f <file_name> -d")
        sys.exit(2)
    
    # Process arguments
    for opt, arg in opts:
        if opt == '-h':
            print("gen_lookup_table.py -n <table_size> -w <WAVE_TYPE> -t <format> -a <amplitude> -f <file_name> -d")
            sys.exit()
        elif opt == '-n':
            TABLE_SIZE = int(arg)
            if TABLE_SIZE < 0:
                print("Table Size must be greater than 0")
                sys.exit()
        elif opt == '-w':
            print(arg.lower())
            if arg.lower() in ALIAS_SINE:
                WAVE_TYPE = Waveform.SINE
            elif arg.lower() in ALIAS_TRI:
                WAVE_TYPE = Waveform.TRI
            elif arg.lower() in ALIAS_RAMP:
                WAVE_TYPE = Waveform.RAMP
            elif arg.lower() in ALIAS_SAW:
                WAVE_TYPE = Waveform.SAW
            elif arg.lower() in ALIAS_SQR:
                WAVE_TYPE = Waveform.SQR
            elif arg.lower() in ALIAS_WHITE:
                WAVE_TYPE = Waveform.WHITE
            else:
                print("Waveform input is invalid, try sine, tri, ramp, saw, sqr, or white noise")
                sys.exit()
        elif opt == '-t':
            if arg == "8":
                FORMAT = Format.SIGNED_8_BIT
                FORMAT_C_STRING = "int8_t"
            elif arg == "16":
                FORMAT = Format.SIGNED_16_BIT
                FORMAT_C_STRING = "int16_t"
            elif arg == "24":
                FORMAT = Format.SIGNED_24_BIT
                FORMAT_C_STRING = "int32_t"
            elif arg == "32":
                FORMAT = Format.SIGNED_32_BIT
                FORMAT_C_STRING = "int32_t"
            elif arg == "32f":
                FORMAT = Format.FLOAT_32_BIT
                FORMAT_C_STRING = "float"
                NP_FORMAT = '\t%f,'
            elif arg == "64f":
                FORMAT = Format.FLOAT_64_BIT
                FORMAT_C_STRING = "float"
                NP_FORMAT = '\t%f,'
            else:
                print("Format input is invalid, try 8, 16, 24, 32, 32f, 64f")
                sys.exit()
        elif opt == '-a':
            try:
                AMPLITUDE = float(arg)
            except:
                print("Invalid amplitude argument, try a float number between -1.0 to 1.0")
                sys.exit()
        elif opt == '-f':
            if arg[-2:] != ".h":
                LOOKUP_TABLE_FILENAME = arg + ".h"
            else:
                LOOKUP_TABLE_FILENAME = arg
        elif opt == '-d':
            DRAW_ENABLED = True

    # Generate Signal
    if WAVE_TYPE == Waveform.SINE:
        wave = Sine(TABLE_SIZE)
    elif WAVE_TYPE == Waveform.TRI:
        wave = Triangle(TABLE_SIZE)
    elif WAVE_TYPE == Waveform.RAMP:
        wave = Saw(TABLE_SIZE)
        wave.set_ramp(True)
    elif WAVE_TYPE == Waveform.SAW:
        wave = Saw(TABLE_SIZE)
        wave.set_ramp(False)
    elif WAVE_TYPE == Waveform.SQR:
        wave = Pulse(TABLE_SIZE)
    elif WAVE_TYPE == Waveform.WHITE:
        wave = WhiteNoise(TABLE_SIZE)
    
    # Write to lookup table with proper format
    if FORMAT == Format.SIGNED_8_BIT:
        lookup_table = wave.process(TABLE_SIZE) * (pow(2, 7) - 1)
    elif FORMAT == Format.SIGNED_16_BIT:
        lookup_table = wave.process(TABLE_SIZE) * (pow(2, 15) - 1)
    elif FORMAT == Format.SIGNED_24_BIT:
        lookup_table = wave.process(TABLE_SIZE) * (pow(2, 23) - 1)
    elif FORMAT == Format.SIGNED_32_BIT:
        lookup_table = wave.process(TABLE_SIZE) * (pow(2, 31) - 1)
    elif FORMAT == Format.FLOAT_32_BIT:
        lookup_table = wave.process(TABLE_SIZE).astype(np.float32)
    elif FORMAT == Format.FLOAT_64_BIT:
        lookup_table = wave.process(TABLE_SIZE).astype(np.float64)
    else:
        print("Something went wrong, exiting")
        sys.exit()

    # Create directory
    path = os.getcwd() + "/lookup_tables"
    if os.path.exists(path) == False:
        try:
            os.mkdir(path)
            print("Making directory " + path)
        except:
            e = sys.exc_info()[0]
            print("Error: %s" % e)

    # Write to file
    print("Writing to %s" % (path + "/" + LOOKUP_TABLE_FILENAME)) 
    np.savetxt(path + "/" + LOOKUP_TABLE_FILENAME, 
            lookup_table, 
            fmt=NP_FORMAT,
            newline='\n', 
            header='#ifndef LOOKUP_H\n#define LOOKUP_H\n\n%s lookup[%d] = {' % (FORMAT_C_STRING, TABLE_SIZE), 
            footer='};\n\n#endif', 
            comments='')

    # Plot
    if DRAW_ENABLED == True:
        print("Plotting...")
        fig, wave_plot = plt.subplots(nrows=1, ncols=1, figsize=(20,10))
        # Signal Plot
        wave_plot.set_title("Lookup Table")
        wave_plot.set_xlabel("Samples")
        wave_plot.set_ylabel("Amplitude")
        wave_plot.plot(np.arange(TABLE_SIZE), lookup_table)
        
        #fig.tight_layout()
        plt.show()

        print("Close GUI to exit program!")
