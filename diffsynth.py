#!/usr/bin/python3
# Copyright © 2015 Bart Massey
# Differential Sound Synthesis


import pyaudio, time, sys
from math import *

class Player():
    sps = 1000
    def __init__(this, nsecs, freq):
        this.pa = pyaudio.PyAudio()
        this.fmt = this.pa.get_format_from_width(1)
        this.paStream = this.pa.open(format=this.fmt,
                        channels=1,
                        rate=this.sps,
                        output=True,
                        stream_callback=(lambda *args:this.callback(*args)))
        this.nWritten = 0
        this.lastFrame = int(nsecs * this.sps)
        this.freq = freq

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
            t = 2 * pi * this.nWritten * this.freq / this.sps
            frames.append(int(64 * sin(t) + 128))
            this.nWritten += 1
        return (bytes(frames), pyaudio.paContinue)

test = Player(3, 400)
while test.isPlaying():
    print(".", end="")
    sys.stdout.flush()
    time.sleep(0.1)
print()
test.close()
