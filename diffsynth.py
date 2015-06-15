#!/usr/bin/python3
# Copyright © 2015 Bart Massey
# [This program is licensed under the "MIT License"]
# Please see the file COPYING in the source
# distribution of this software for license terms.

# Differential Sound Synthesis


import pyaudio, time, sys
from math import *

def shift_div(v, s):
    if v < 0:
        return -(-v >> s)
    else:
        return v >> s

class SinSynth():
    def __init__(this, freq):
        this.freq = freq

    def register(this, player):
        this.player = player

    def synthesize(this, i):
        t = 2 * pi * i * this.freq / this.player.sps
        return int(64 * sin(t))

def clamp_unsigned(v):
    if v > 255:
        v = 255
    if v < 0:
        v = 0
    return v

def clamp_signed(v):
    if v > 127:
        v = 127
    if v < -128:
        v = -128
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
        d1 = shift_div(v1 - v0, 0)
        d2 = shift_div(v2 - v1, 0)
        dd = shift_div(d1 - d2, 1)
        v = clamp_signed(-dd)
        this.ring[i0] = v
        this.ptr = i1
        return v


class FlatSynth():
    def __init__(this, shift):
        this.shift = shift

    def register(this, player):
        pass

    def synthesize(this, i):
        return this.shift

class ExpDecaySynth():
    def __init__(this):
        this.ticks = 0
        this.shift = 0

    def register(this, player):
        this.interval = int(player.nsecs * player.sps) >> 2

    def synthesize(this, i):
        if this.ticks >= this.interval:
            this.interval >>= 1
            this.ticks = 0
            this.shift += 1
        this.ticks += 1
        return this.shift

class AttackDecaySynth():
    def __init__(this):
        this.ticks = 0
        this.shift = 0
        this.rising = True

    def register(this, player):
        this.samples = int(player.nsecs * player.sps)
        this.interval = this.samples >> 2

    def synthesize(this, i):
        if this.ticks >= this.interval:
            if this.rising and this.shift <= 0:
                this.rising = False
                this.interval = this.samples >> 2
            else:
                this.interval >>= 1
                if this.rising:
                    this.shift -= 1
                else:
                    this.shift += 1
            this.ticks = 0
        else:
            this.ticks += 1
        return this.shift

class TriangleSynth():
    def __init__(this):
        this.ticks = 0

    def register(this, player):
        this.samples = int(player.nsecs * player.sps)
        this.interval = this.samples >> 4
        this.shift = 8
        print(this.shift)

    def synthesize(this, i):
        if this.ticks >= this.interval:
            this.ticks = 0
            if i >= (this.samples >> 1):
                this.shift += 1
            else:
                this.shift -= 1
            print(i, this.shift)
        this.ticks += 1
        return min(this.shift, 6)

class Player():
    def __init__(this, sps, synths, nsecs, envelope = None):
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
        this.nsecs = nsecs
        for synth in synths:
            synth.register(this)
        this.synths = synths
        this.envelope = envelope
        if envelope:
            envelope.register(this)

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
            if this.envelope:
                e = this.envelope.synthesize(this.nWritten)
                v = shift_div(v, e)
            v = clamp_unsigned(v + 128)
            frames.append(v)
            this.nWritten += 1
        # sys.stdout.buffer.write(bytes(frames))
        return (bytes(frames), pyaudio.paContinue)

#synths = [SinSynth(400)]
synths = [LizardSynth(32, [(0, 127), (0.3, 63), (0.6, 31)])]
#synth1 = LizardSynth(63, [(0, 127)])
#synth2 = LizardSynth(13, [(0.5, 63)])
#synths = [synth1, synth2]
#ad = FlatSynth(0)
ad = ExpDecaySynth()
#ad = AttackDecaySynth()
#ad = TriangleSynth()
test = Player(1000, synths, 4, envelope = ad)
while test.isPlaying():
    print(".", end="")
    sys.stdout.flush()
    time.sleep(0.1)
print()
test.close()
