import numpy as np
import sounddevice as sd

RATE = 44100  # Sample rate
duration = 1.0  # Duration per note in seconds
A4 = 440.0  # A440 Hz

HALF_STEP = np.power(2, 1/12)

notes_active = []
samples_read = 0

class Note:
    def __init__(self, frequency, start, end):
        self.frequency = frequency
        self.start = start
        self.end = end

def callback(outdata, frames, _, status):
    data = np.zeroes(frames)

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

        decay_rate = 3
        decay = np.exp(-decay_rate * (timestamps_relative_to_this_note))
        note_wave_raw = 0.5 * np.sin(2 * np.pi * note.frequency *(timestamps_relative_to_this_note)/ RATE) * decay

        # Zero out everything that isn't an active timestamp.
        note_wave = np.where(active_timestamps, note_wave_raw, 0)

        data += note_wave

    notes_active[:] = notes_still_active
    outdata[:, 0] = data

stream = sd.OutputStream(samplerate=RATE, channels=1, callback=callback)
stream.start()

