from pylibpd import *

import array
import pygame
import numpy

BUFFERSIZE=4096
SAMPLERATE=44100
BLOCKSIZE=64

pygame.mixer.init(frequency=SAMPLERATE)

m = PdManager(1, 2, SAMPLERATE, 1)
patch = libpd_open_patch('test.pd', '.')
print "$0: ", patch

inbuf = array.array('h', range(BLOCKSIZE)) # signed short/int/2 bytes/16bit

# fetch a mixer channel to feed samples in
ch = pygame.mixer.Channel(0)

# initialize the sample buffers we are going to use
sounds = [pygame.mixer.Sound(numpy.zeros((BUFFERSIZE, 2), numpy.int16)) for s in range(2)]
samples = [pygame.sndarray.samples(s) for s in sounds]

# select one of the buffers after another
selector = 0
while(1):
    # there is no(thing in the) queue, so let's fill it up
    if not ch.get_queue():
        for x in range(BUFFERSIZE):
            if x % BLOCKSIZE == 0:
                # grab a block of audio from Pd
                outbuf = m.process(inbuf)
            # data from PD is coming interlaced, i.e. sample1/channel1, sample1/channel2, sample2/channel1, sample2/channel2 ...    
            samples[selector][x][0] = outbuf[(x % BLOCKSIZE) * 2]
            samples[selector][x][1] = outbuf[(x % BLOCKSIZE) * 2 + 1]
        # queue it up for playback    
        ch.queue(sounds[selector])

        # alternate buffer next round
        selector = int(not(selector))

libpd_release()
