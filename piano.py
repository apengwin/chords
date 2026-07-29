import time
import threading

import numpy as np
import sounddevice as sd

RATE = 44100  # Sample rate
duration = 1.0  # Duration per note in seconds
A = 440.0  # A440 Hz

HALF_STEP = np.power(2, 1/12)

NOTES = {
    "C": A * np.pow(HALF_STEP, -9),
    "D": A * np.pow(HALF_STEP, -7),
    "E": A * np.pow(HALF_STEP, -5),
    "F": A * np.pow(HALF_STEP, -4),
    "G": A * np.pow(HALF_STEP, -2),
    "A": A,
    "B": A * HALF_STEP,
    # Use the weird german nomenclature so we at least get another note
    "H": A * np.pow(HALF_STEP, 2)
} 

DECAY_RATE = 5

notes_active = []
samples_read = 0

class Note:
    def __init__(self, frequency, start, end):
        self.frequency = frequency
        self.start = start
        self.end = end

def callback(outdata, frames, _, status):
    global samples_read

    data = np.zeros(frames)

    notes_still_active = []

    # The absolute timestamps of the audio segment to return
    timestamps = (np.arange(frames) + samples_read)

    for note in notes_active:
        if note.end < samples_read:
            continue

        notes_still_active.append(note)

        # For this note, the timestamps that it is making a sound
        active_timestamps = (timestamps  > note.start) & (timestamps< note.end)

        # Note that timestamps - note.start should give an array of how far into the note we are.
        # It is an array of consecutive integers, where the index where the value is 0 corresponds
        # the index of timestamps where the note begins.
        timestamps_relative_to_this_note = timestamps - note.start
        decay = np.exp(-1 * DECAY_RATE * (timestamps_relative_to_this_note / RATE))

        # Construct a note by 
        #   1. creating the sine wave with the note frequency
        #   2. adding some decay.
        # But we need to account for the fact that the callback could have been called mid-note.
        # The values of the sine wave and the dceay have to be calculated relative to the position where we are in
        # this note's lifetime.
        note_wave_raw = np.sin(2 * np.pi * note.frequency *(timestamps_relative_to_this_note)/ RATE) * decay

        # Zero out everything that isn't an active timestamp.
        note_wave = np.where(active_timestamps, note_wave_raw, 0)

        data += note_wave

    samples_read += frames
    notes_active[:] = notes_still_active
    outdata[:, 0] = data

def seed_notes():
    notes_active.append(Note(NOTES["C"], 0, RATE * 3))
    notes_active.append(Note(A * 1.5, RATE /10, RATE * 5))
    
def play(note):
    notes_active.append(Note(NOTES[note], samples_read, samples_read + RATE * duration))


#seed_notes()
stream = sd.OutputStream(samplerate=RATE, channels=1, callback=callback)
stream.start()
play("A")
time.sleep(0.03)
play("H")


while True:
    pass
