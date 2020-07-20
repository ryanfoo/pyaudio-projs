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
SAMPLE_RATE = 44100
# ms linear spacing
TIME_DOMAIN_XS = np.linspace(0, int(NUM_FRAMES / SAMPLE_RATE * 1000), NUM_FRAMES)
FREQ_DOMAIN_XS = np.linspace(0, int(SAMPLE_RATE / 2), int(NUM_FRAMES / 2))

fig, waves = plt.subplots(8, 2, figsize=(16, 10))
fig.suptitle("Naive Waveforms")

# Test Sine wave
sine = Sine(SAMPLE_RATE)
sine.set_frequency(440.)
samples = sine.process(NUM_FRAMES)
waves[0][0].plot(TIME_DOMAIN_XS, samples)
waves[0][1].plot(FREQ_DOMAIN_XS, 2.0 / NUM_FRAMES * np.abs(fft(samples)[:int(NUM_FRAMES / 2)]))

# Test Pulse wave 50%
sqr = Pulse(SAMPLE_RATE)
sqr.set_frequency(440.)
samples = sqr.process(NUM_FRAMES)
waves[1][0].plot(TIME_DOMAIN_XS, samples)
waves[1][1].plot(FREQ_DOMAIN_XS, 2. / NUM_FRAMES * np.abs(fft(samples)[:int(NUM_FRAMES / 2)]))

# Test Pulse wave 10%
sqr.reset()
sqr.set_duty_cycle(0.10)
samples = sqr.process(NUM_FRAMES)
waves[2][0].plot(TIME_DOMAIN_XS, samples)
waves[2][1].plot(FREQ_DOMAIN_XS, 2. / NUM_FRAMES * np.abs(fft(samples)[:int(NUM_FRAMES / 2)]))

# Test Pulse wave 75%
sqr.reset()
sqr.set_duty_cycle(0.75)
samples = sqr.process(NUM_FRAMES)
waves[3][0].plot(TIME_DOMAIN_XS, samples)
waves[3][1].plot(FREQ_DOMAIN_XS, 2. / NUM_FRAMES * np.abs(fft(samples)[:int(NUM_FRAMES / 2)]))

# Test Triangle wave
tri = Triangle(SAMPLE_RATE)
tri.set_frequency(440.)
samples = tri.process(NUM_FRAMES)
waves[4][0].plot(TIME_DOMAIN_XS, samples)
waves[4][1].plot(FREQ_DOMAIN_XS, 2. / NUM_FRAMES * np.abs(fft(samples)[:int(NUM_FRAMES / 2)]))

# Test ramp up wave
saw = Saw(SAMPLE_RATE)
saw.set_frequency(440.)
samples = saw.process(NUM_FRAMES)
waves[5][0].plot(TIME_DOMAIN_XS, samples)
waves[5][1].plot(FREQ_DOMAIN_XS, 2. / NUM_FRAMES * np.abs(fft(samples)[:int(NUM_FRAMES / 2)]))

# Test ramp down wave
saw.reset()
saw.set_ramp(False)
samples = saw.process(NUM_FRAMES)
waves[6][0].plot(TIME_DOMAIN_XS, samples)
waves[6][1].plot(FREQ_DOMAIN_XS, 2. / NUM_FRAMES * np.abs(fft(samples)[:int(NUM_FRAMES / 2)]))

# Test White Noise
whiteNoise = WhiteNoise(SAMPLE_RATE)
samples = whiteNoise.process(NUM_FRAMES)
waves[7][0].plot(TIME_DOMAIN_XS, samples)
waves[7][1].plot(FREQ_DOMAIN_XS, 2. / NUM_FRAMES * np.abs(fft(samples)[:int(NUM_FRAMES / 2)]))

plt.show()