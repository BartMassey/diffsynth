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

class Player():
    sps = 1000
    def __init__(this, synth, nsecs):
        this.pa = pyaudio.PyAudio()
        this.fmt = this.pa.get_format_from_width(1)
        this.paStream = this.pa.open(format=this.fmt,
                        channels=1,
                        rate=this.sps,
                        output=True,
                        stream_callback=(lambda *args:this.callback(*args)))
        this.nWritten = 0
        this.lastFrame = int(nsecs * this.sps)
        synth.register(this)
        this.synth = synth

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
            frames.append(this.synth.synthesize(this.nWritten))
            this.nWritten += 1
        return (bytes(frames), pyaudio.paContinue)

synth = SinSynth(400)
test = Player(synth, 3)
while test.isPlaying():
    print(".", end="")
    sys.stdout.flush()
    time.sleep(0.1)
print()
test.close()
