# Differential Synthesis
Copyright © 2015 Bart Massey

This little Python 3 demo uses the
[PyAudio](https://people.csail.mit.edu/hubert/pyaudio/)
library to play a rich sound obtained by "Differential
Synthesis".

Differential Synthesis essentially numerically solves a
differential equation with delay to get an oscillating
signal without multiplies and without much memory. While I
have invented and named the technique independently, I am
sure it is quite common in the sound synthesis literature.

The current implementation runs with 32 bytes of buffer and
produces 8-bit unsigned audio samples using 8-bit
operations. The synthesis frequency is adjustable, but is
presently set to 1KHz. An envelope is also generated, using
shift operations to adjust the volume.

The sound currently being output is intended for use in an
e-jewelry [project](http://github.com/BartMassey/lizard)
utilizing a slowish 8-bit processor.

This program is licensed under the "MIT License".  Please
see the file COPYING in the source distribution of this
software for license terms.
