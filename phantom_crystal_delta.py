import numpy as np
from scipy.io import wavfile

# --- File Architecture ---
duration = 1800.0    # 30 minutes of runtime
sample_rate = 44100  # High-fidelity CD quality

# --- The Physics-Delta Matrix ---
f_crystal = np.array([132.0, 423.0, 555.0]) # Core Earth-field frequencies
f_target_beat = 2.0                          # Target Delta state (Hz)
offset = f_target_beat / 2.0                 # Symmetrical split (1.0 Hz)

# Time array synthesis
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

# Initialize stereo tracks
left_channel = np.zeros_like(t)
right_channel = np.zeros_like(t)

# Normalize gain to 0.3 per carrier to completely eliminate digital clipping
amplitude = 0.3 

# --- Synthesize Symmetrical Waveforms ---
for f_center in f_crystal:
    # Left channel handles the upper boundary shift
    left_channel += amplitude * np.sin(2 * np.pi * (f_center + offset) * t)
    # Right channel handles the lower boundary shift
    right_channel += amplitude * np.sin(2 * np.pi * (f_center - offset) * t)

# Interleave channels into a unified stereo array
stereo_data = np.vstack((left_channel, right_channel)).T

# Cast to 16-bit PCM for universal hardware playback
stereo_data = (stereo_data * 32767).astype(np.int16)

# Compile and export
output_filename = "entropy_flush_delta_2hz.wav"
wavfile.write(output_filename, sample_rate, stereo_data)

print(f"Matrix compiled successfully: '{output_filename}'")
print(f"Left Ear Spectrum:  {f_crystal + offset} Hz")
print(f"Right Ear Spectrum: {f_crystal - offset} Hz")
print(f"Synthesized Biological Intercept: {f_target_beat} Hz Delta Entropy Flush")