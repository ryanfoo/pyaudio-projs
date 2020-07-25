'''
    File Name: oscillator_tests.py
    Author: Ryan Foo
    Date created: 07/19/2020
    Python Version: 3.7

    Tests tone.py functions/classes. Draws the time domain and frequency domain waveforms/spectrums

    Plots's x-axis is in ms scale (time domain), hz scale (freq domain)
    Plots's y-axis is in amplitude scale (time domain + freq domain)
'''

#!/usr/bin/python

from matplotlib import pyplot as plt

import sys
import time

import numpy as np
import pyaudio
from scipy.fftpack import fft

from oscillator import *

##TODO: Write unit tests; Compare processed output with valid input text file

NUM_FRAMES = 1024
SAMPLE_RATE = 1024
# Show 4 cycles
FREQ = 4.
# ms linear spacing
TIME_DOMAIN_XS = np.linspace(0, int(NUM_FRAMES / SAMPLE_RATE), NUM_FRAMES)
FREQ_DOMAIN_XS = np.linspace(0, int(SAMPLE_RATE / 2), int(NUM_FRAMES / 2))

fig, waves = plt.subplots(nrows=8, ncols=2, figsize=(20, 10))
#fig.suptitle("Naive Waveforms")

# Test Sine wave
sine = Sine(SAMPLE_RATE)
sine.set_frequency(FREQ)
samples = sine.process(NUM_FRAMES)
waves[0][0].set_title("Sine Wave (Time)")
waves[0][0].set_xlabel("Time (s)")
waves[0][0].set_ylabel("Amplitude")
waves[0][0].plot(TIME_DOMAIN_XS, samples)
waves[0][1].set_title("Sine Wave (Spectrum)")
waves[0][1].set_xlabel("Frequency (Hz)")
waves[0][1].set_ylabel("Amplitude")
waves[0][1].plot(FREQ_DOMAIN_XS, 2.0 / NUM_FRAMES * np.abs(fft(samples)[:int(NUM_FRAMES / 2)]))

# Test Pulse wave 50%
sqr = Pulse(SAMPLE_RATE)
sqr.set_frequency(FREQ)
samples = sqr.process(NUM_FRAMES)
waves[1][0].set_title("Pulse Wave 50% (Time)")
waves[1][0].set_xlabel("Time (s)")
waves[1][0].set_ylabel("Amplitude")
waves[1][0].plot(TIME_DOMAIN_XS, samples)
waves[1][1].set_title("Pulse Wave 50% (Spectrum)")
waves[1][1].set_xlabel("Frequency (Hz)")
waves[1][1].set_ylabel("Amplitude")
waves[1][1].plot(FREQ_DOMAIN_XS, 2. / NUM_FRAMES * np.abs(fft(samples)[:int(NUM_FRAMES / 2)]))

# Test Pulse wave 10%
sqr.reset()
sqr.set_duty_cycle(0.10)
samples = sqr.process(NUM_FRAMES)
waves[2][0].set_title("Pulse Wave 10% (Time)")
waves[2][0].set_xlabel("Time (s)")
waves[2][0].set_ylabel("Amplitude")
waves[2][0].plot(TIME_DOMAIN_XS, samples)
waves[2][1].set_title("Pulse Wave 10% (Spectrum)")
waves[2][1].set_xlabel("Frequency (Hz)")
waves[2][1].set_ylabel("Amplitude")
waves[2][1].plot(FREQ_DOMAIN_XS, 2. / NUM_FRAMES * np.abs(fft(samples)[:int(NUM_FRAMES / 2)]))

# Test Pulse wave 75%
sqr.reset()
sqr.set_duty_cycle(0.75)
samples = sqr.process(NUM_FRAMES)
waves[3][0].set_title("Pulse Wave 75% (Time)")
waves[3][0].set_xlabel("Time (s)")
waves[3][0].set_ylabel("Amplitude")
waves[3][0].plot(TIME_DOMAIN_XS, samples)
waves[3][1].set_title("Pulse Wave 75% (Spectrum)")
waves[3][1].set_xlabel("Frequency (Hz)")
waves[3][1].set_ylabel("Amplitude")
waves[3][1].plot(FREQ_DOMAIN_XS, 2. / NUM_FRAMES * np.abs(fft(samples)[:int(NUM_FRAMES / 2)]))

# Test Triangle wave
tri = Triangle(SAMPLE_RATE)
tri.set_frequency(FREQ)
samples = tri.process(NUM_FRAMES)
waves[4][0].set_title("Triangle Wave (Time)")
waves[4][0].set_xlabel("Time (s)")
waves[4][0].set_ylabel("Amplitude")
waves[4][0].plot(TIME_DOMAIN_XS, samples)
waves[4][1].set_title("Triangle Wave (Spectrum)")
waves[4][1].set_xlabel("Frequency (Hz)")
waves[4][1].set_ylabel("Amplitude")
waves[4][1].plot(FREQ_DOMAIN_XS, 2. / NUM_FRAMES * np.abs(fft(samples)[:int(NUM_FRAMES / 2)]))

# Test ramp up wave
saw = Saw(SAMPLE_RATE)
saw.set_frequency(FREQ)
samples = saw.process(NUM_FRAMES)
waves[5][0].set_title("Ramp Wave (Time)")
waves[5][0].set_xlabel("Time (s)")
waves[5][0].set_ylabel("Amplitude")
waves[5][0].plot(TIME_DOMAIN_XS, samples)
waves[5][1].set_title("Ramp Wave (Spectrum)")
waves[5][1].set_xlabel("Frequency (Hz)")
waves[5][1].set_ylabel("Amplitude")
waves[5][1].plot(FREQ_DOMAIN_XS, 2. / NUM_FRAMES * np.abs(fft(samples)[:int(NUM_FRAMES / 2)]))

# Test ramp down wave
saw.reset()
saw.set_ramp(False)
samples = saw.process(NUM_FRAMES)
waves[6][0].set_title("Sawtooth Wave (Time)")
waves[6][0].set_xlabel("Time (s)")
waves[6][0].set_ylabel("Amplitude")
waves[6][0].plot(TIME_DOMAIN_XS, samples)
waves[6][1].set_title("Sawtooth Wave (Spectrum)")
waves[6][1].set_xlabel("Frequency (Hz)")
waves[6][1].set_ylabel("Amplitude")
waves[6][1].plot(FREQ_DOMAIN_XS, 2. / NUM_FRAMES * np.abs(fft(samples)[:int(NUM_FRAMES / 2)]))

# Test White Noise
whiteNoise = WhiteNoise(SAMPLE_RATE)
samples = whiteNoise.process(NUM_FRAMES)
waves[7][0].set_title("White Noise (Time)")
waves[7][0].set_xlabel("Time (s)")
waves[7][0].set_ylabel("Amplitude")
waves[7][0].plot(TIME_DOMAIN_XS, samples)
waves[7][1].set_title("White Noise (Spectrum)")
waves[7][1].set_xlabel("Frequency (Hz)")
waves[7][1].set_ylabel("Amplitude")
waves[7][1].plot(FREQ_DOMAIN_XS, 2. / NUM_FRAMES * np.abs(fft(samples)[:int(NUM_FRAMES / 2)]))

# Evenly space the graphs
fig.tight_layout()
# Show plots
plt.show()