#!/bin/sh
./lizardsynth |
sox -c 1 -r 1000 -t s8 - \
    -r 4000 lizard-noise.wav &&
aplay lizard-noise.wav
