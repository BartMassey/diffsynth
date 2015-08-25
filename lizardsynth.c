/* Copyright © 2015 Bart Massey */
/* "Lizard Noise" differential synthesizer
 * C.f. http://github.com/BartMassey/diffsynth */
/* [This program is licensed under the "MIT License"]
   Please see the file COPYING in the source
   distribution of this software for license terms. */

#include <stdint.h>
#include <stdio.h>

#define LIZARD_RING_SIZE 32

typedef int8_t sample_t;
typedef int calc_t;

calc_t shift_div(calc_t v, calc_t s) {
    if (v < 0)
        return -(-v >> s);
    return v >> s;
}

sample_t clamp_signed(calc_t v) {
    if (v > 127)
        return 127;
    if (v < -127)
        return -127;
    return (int8_t)v;
}

typedef struct ring {
    sample_t ring_vs[LIZARD_RING_SIZE];
    uint8_t ring_nvs;
    uint8_t ring_ptr;
} ring_t;

uint8_t inc(uint8_t nvs, uint8_t ptr) {
    ptr += 1;
    while (ptr >= nvs)
        ptr -= nvs;
    return ptr;
}

sample_t lizard_synth(ring_t *ring) {
    uint8_t i0 = ring->ring_ptr;
    uint8_t i1 = inc(ring->ring_nvs, i0);
    uint8_t i2 = inc(ring->ring_nvs, i1);
    sample_t v0 = ring->ring_vs[i0];
    sample_t v1 = ring->ring_vs[i1];
    sample_t v2 = ring->ring_vs[i2];
    calc_t d1 = v1 - v0;
    calc_t d2 = v2 - v1;
    calc_t dd = shift_div(d1 - d2, 1);
    sample_t v = clamp_signed(-dd);
    ring->ring_vs[i0] = v;
    ring->ring_ptr = i1;
    return v;
}

void lizard_synth_init_ring(ring_t *ring) {
    int i;
    ring->ring_nvs = LIZARD_RING_SIZE;
    ring->ring_ptr = 0;
    for (i = 0; i < ring->ring_nvs; i++)
        ring->ring_vs[i] = 0;
    ring->ring_vs[0] = 127;
    ring->ring_vs[11] = 63;
    ring->ring_vs[23] = 32;
}

ring_t lizard_ring;

int main(void) {
    int i;
    lizard_synth_init_ring(&lizard_ring);
    for (i = 0; i < 1000; i++) {
        sample_t v = lizard_synth(&lizard_ring);
        fwrite(&v, sizeof(v), 1, stdout);
    }
    return 0;
}
