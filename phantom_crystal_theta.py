import numpy as np
from scipy.io import wavfile

# --- Configuration ---
duration = 1800.0    # 30 minutes
sample_rate = 44100  # CD Quality

# --- The Symmetrical Physics Grid ---
f_crystal = np.array([132.0, 423.0, 555.0]) # The target Earth-field centers
f_target_beat = 6.0                          # Target Theta brainwave (Hz)
offset = f_target_beat / 2.0                 # Equal split (3.0 Hz)

# Time vector
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

# Initialize blank stereo arrays
left_channel = np.zeros_like(t)
right_channel = np.zeros_like(t)

# Normalize amplitude to prevent digital clipping when summing the triad
amplitude = 0.3 

# --- Synthesize Phantom Crystal Matrix ---
for f_center in f_crystal:
    # Left ear is staggered UP by half the target beat
    left_channel += amplitude * np.sin(2 * np.pi * (f_center + offset) * t)
    # Right ear is staggered DOWN by half the target beat
    right_channel += amplitude * np.sin(2 * np.pi * (f_center - offset) * t)

# Interleave the mono arrays into a single stereo track
stereo_data = np.vstack((left_channel, right_channel)).T

# Convert to 16-bit PCM for standard WAV compatibility
stereo_data = (stereo_data * 32767).astype(np.int16)

# Export file
output_filename = "phantom_crystal_theta_6hz.wav"
wavfile.write(output_filename, sample_rate, stereo_data)

print(f"Success! '{output_filename}' generated.")
print(f"Left Ear Range:  {f_crystal + offset} Hz")
print(f"Right Ear Range: {f_crystal - offset} Hz")
print(f"Symmetrical Brainwave Intercept: {f_target_beat} Hz")