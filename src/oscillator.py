'''
    File Name: tone.py
    Author: Ryan Foo
    Date created: 07/19/2020
    Python Version: 3.7

    Naive realtime generation

    TODO: Add checks on set methods
'''

#!/usr/bin/python

from abc import ABC, abstractmethod
from enum import Enum
import sys
import numpy as np

'''
Abstract class for tone generation classes
'''
class Oscillator(ABC):
    # Constructor
    def __init__(self, srate = 44100, f = 1., a = 1.):
        self.sample_rate    = srate
        self.amplitude      = a
        self.frequency      = f
        # Start frame offset at 1; don't calculate at frame 0 due to zero division
        self.frame_offset   = 1

    # Set sample rate
    def set_samplerate(self, srate):
        self.sample_rate = srate

    # Set amplitude
    def set_amplitude(self, a):
        self.amplitude = a

    # Set frequency
    def set_frequency(self, f):
        self.frequency = f

    # Reset frame offset
    def reset(self):
        self.frame_offset = 1

    # Display member variables
    def display(self):
        print("Member Variables\n---------------\nSample Rate = %d\nAmplitude = %f\nFrequency = %f" % (self.sample_rate, self.amplitude, self.frequency))

    # This must be defined in subclasses
    @abstractmethod
    def process(self, frames):
        '''Processing / calculate phases per frame'''
        pass

'''
Naive Realtime Sine wave generation subclass
Note: Can optimize with wavetables
'''
class Sine(Oscillator):
    ''' Private Variables '''
    __omega = 0

    def __init__(self, srate = 44100, f = 1., a = 1.):
        super(Sine, self).__init__(srate, f, a)
        self.set_frequency(f)
 
    def set_frequency(self, f):
        super(Sine, self).set_frequency(f)
        self.__omega = 2. * np.pi * self.frequency / self.sample_rate

    def process(self, frames):
        samples = self.amplitude * np.sin(np.arange(self.frame_offset, self.frame_offset + frames) * self.__omega)
        self.frame_offset += frames
        return samples

'''
Naive Realtime Triangle wave generation subclass
Function taken from wikipedia
y(x) = (2 * a / pi) * arcsin(sin(2 * pi * x / period))

Note: This is not bandlimited so will encounter aliasing issues.
'''
class Triangle(Oscillator):
    ''' Private Variables '''
    __omega = 0

    def __init__(self, srate = 44100, f = 1., a = 1.):
        super(Triangle, self).__init__(srate, f, a)
        self.set_frequency(f)

    def set_frequency(self, f):
        super(Triangle, self).set_frequency(f)
        self.__omega = 2. * np.pi * self.frequency / self.sample_rate

    def process(self, frames):
        samples = (2 * self.amplitude / np.pi) * np.arcsin(np.sin(self.__omega * np.arange(self.frame_offset, self.frame_offset + frames)))
        self.frame_offset += frames
        return samples

'''
Naive Realtime Sawtooth wave generation subclass
Function taken from wikipeida
y(x) = -(2 * a / pi) * arctan(cot(pi * x / period))

Note: This is not bandlimited so will encounter aliasing issues.
'''
class Saw(Oscillator):
    ''' Private Variables '''
    __omega = 0

    # Ramp Polarity
    class Ramp(Enum):
        UP = 1
        DOWN = 2

    __ramp = Ramp.UP

    def __init__(self, srate = 44100, f = 1., a = 1.):
        super(Saw, self).__init__(srate)
        self.set_frequency(f)

    def set_frequency(self, f):
        super(Saw, self).set_frequency(f)
        self.__omega = np.pi * self.frequency / self.sample_rate

    def set_ramp(self, r):
        if r == True:
            self.__ramp = self.Ramp.UP
        else:
            self.__ramp = self.Ramp.DOWN

    def process(self, frames):
        if self.__ramp == self.Ramp.UP:
            samples = -(2 * self.amplitude / np.pi) * np.arctan(1. / np.tan(self.__omega * np.arange(self.frame_offset, self.frame_offset + frames)))
        else:
            samples = ((self.amplitude / 2) - (self.amplitude / np.pi)) * np.arctan(1. / np.tan(self.__omega * np.arange(self.frame_offset, self.frame_offset + frames)))
        self.frame_offset += frames
        return samples
'''
Naive Realtime Square wave generation subclass

Note: This is not bandlimited so will encounter aliasing issues.
'''
class Pulse(Oscillator):
    ''' Private Variables '''
    __duty_cycle = 0.5
    __dc_constant = 0
    __omega = 0

    def __init__(self, srate = 44100, f = 1., a = 1., dc = 0.5):
        super(Pulse, self).__init__(srate)
        self.__duty_cycle = dc
        self.set_frequency(f)

    def set_frequency(self, f):
        super(Pulse, self).set_frequency(f)
        self.__omega = 2. * np.pi * self.frequency / self.sample_rate

    def set_duty_cycle(self, dc):
        self.__duty_cycle = dc
        self.__dc_constant = -(2 * self.__duty_cycle) + 1

    def process(self, frames):
        samples = np.sin(np.arange(self.frame_offset, self.frame_offset + frames) * self.__omega)
        self.frame_offset += frames
        #TODO: Should probably calculate the duty cycle in time domain, not in this piecewise function
        return self.amplitude * np.piecewise(samples, [samples >= self.__dc_constant, samples < self.__dc_constant], [1, -1])

'''
Naive Realtime White Noise generation subclass

TODO: Verify equal intensity over frequency spectrum
'''
class WhiteNoise(Oscillator):
    def __init__(self, srate = 44100):
        super(WhiteNoise, self).__init__(srate)
 
    def process(self, frames):
        return 2. * np.random.rand(frames) - 1.