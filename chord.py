from music21 import note, stream
from music21 import environment
import numpy as np
import scipy.io.wavfile
from scipy.signal import find_peaks

env = environment.UserSettings()
env["lilypondPath"] = "/opt/homebrew/bin/lilypond"

sample_rate, signal = scipy.io.wavfile.read("/Users/allan/Downloads/cmajor_mono.wav")
signal = signal.astype(np.float64)

# window to reduce spectral leakage
# hanning window because
windowed = signal * np.hanning(len(signal))

fft = np.abs(np.fft.rfft(windowed))
freqs = np.fft.rfftfreq(len(signal), d=1 / sample_rate)

# normalize
fft_normalized = fft / np.max(fft)

# find peaks above a threshold, with some minimum spacing
peaks, properties = find_peaks(fft_normalized, height=0.1, distance=20)

# map frequencies to canonical note
def freq_to_note(freq):
    A4 = 440.0 
    if freq <= 0:
        return None
    steps_relative_A4 = 12 * np.log2(freq / A4)
    NOTES = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
    note_index = round(steps_relative_A4) % 12
    octave = 4 + (round(steps_relative_A4) + 9) // 12
    return f"{NOTES[note_index]}{octave}"


# filter to piano range and print
score = stream.Stream()
for peak in peaks:
    f = freqs[peak]
    if 440 / 16 < f < 440 * 8: # Filter out notes not between A0 -> A7
        n = freq_to_note(f)
        print(f"{n:>4s}  {f:7.2f} Hz  (magnitude: {fft_normalized[peak]:.2f})")

        if (fft_normalized[peak]) > 0.7:
            score.append(note.Note(n, quarterLength=1.0))

score.show("lily")
