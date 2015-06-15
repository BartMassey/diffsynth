#!/usr/bin/python3
# Copyright © 2015 Bart Massey
# Differential Sound Synthesis


import pyaudio, time, sys
from math import *

class SinSynth():
    def __init__(this, freq):
        this.freq = freq

    def register(this, player):
        this.player = player

    def synthesize(this, i):
        t = 2 * pi * i * this.freq / this.player.sps
        return int(64 * sin(t) + 128)

def clamp(v):
    v += 128
    if v > 255:
        v = 255
    if v < 0:
        v = 0
    return v

class LizardSynth():
    def __init__(this, ring_size, inits):
        this.ringSize = ring_size
        this.inits = inits

    def register(this, player):
        this.player = player
        this.ring = [0] * this.ringSize
        for (i, v) in this.inits:
            this.ring[int(i * this.ringSize)] = v
        this.ptr = 0

    def inc(this, ptr):
        ptr += 1
        while ptr >= this.ringSize:
            ptr -= this.ringSize
        return ptr

    def synthesize(this, i):
        i0 = this.ptr
        i1 = this.inc(i0)
        i2 = this.inc(i1)
        v0 = this.ring[i0]
        v1 = this.ring[i1]
        v2 = this.ring[i2]
        d1 = (v1 - v0) >> 1
        d2 = (v2 - v1) >> 1
        dd = (d1 - d2) >> 1
        v = clamp(-dd)
        this.ring[i0] = v
        this.ptr = i1
        return v


class Player():
    def __init__(this, sps, synths, nsecs):
        this.sps = sps
        this.pa = pyaudio.PyAudio()
        this.fmt = this.pa.get_format_from_width(1)
        this.paStream = this.pa.open(format=this.fmt,
                        channels=1,
                        rate=this.sps,
                        output=True,
                        stream_callback=(lambda *args:this.callback(*args)))
        this.nWritten = 0
        this.lastFrame = int(nsecs * this.sps)
        for synth in synths:
            synth.register(this)
        this.synths = synths

    def start(this):
        this.paStream.start_stream()

    def isPlaying(this):
        return this.nWritten < this.lastFrame or this.paStream.is_active()

    def close(this):
        this.paStream.stop_stream()
        this.paStream.close()
        this.pa.terminate()
    
    def callback(this, in_data, frame_count, time_info, status):
        if this.nWritten >= this.lastFrame:
            return (bytes(), pyaudio.paComplete)
        frames = bytearray()
        for i in range(frame_count):
            if this.nWritten >= this.lastFrame:
                frames += bytearray([128] * (frame_count - i))
                break
            v = 0
            for synth in this.synths:
                v += synth.synthesize(this.nWritten)
            v //= len(this.synths)
            frames.append(v)
            this.nWritten += 1
        return (bytes(frames), pyaudio.paContinue)

#synth = SinSynth(400)
#synth = LizardSynth([(0, 127), (0.3, 63), (0.6, 31)])
synth1 = LizardSynth(32, [(0, 127)])
synth2 = LizardSynth(13, [(0.5, 63)])
test = Player(1000, [synth1, synth2], 4)
while test.isPlaying():
    print(".", end="")
    sys.stdout.flush()
    time.sleep(0.1)
print()
test.close()
