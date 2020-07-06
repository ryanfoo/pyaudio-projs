#!/usr/bin/python

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
# Need 1.4
#from matplotlib import style

#style.use('fivethirtyeight')

BUFFER_SIZE = 5000

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
idx = 0

def animate(i):
    xs = np.arange(idx, idx+BUFFER_SIZE)
    # Random
    #ys = np.random.rand(BUFFER_SIZE)
    # Sine
    ys = 0.75 * np.sin(2. * np.pi * 25. / 44100. * xs)
    ax1.clear()
    ax1.plot(xs, ys)

ani = animation.FuncAnimation(fig, animate, BUFFER_SIZE)
plt.show()
