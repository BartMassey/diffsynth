CC = gcc
CFLAGS = -g -Wall

lizardsynth: lizardsynth.c
	$(CC) $(CFLAGS) -o lizardsynth lizardsynth.c

clean:
	-rm -f lizardsynth
