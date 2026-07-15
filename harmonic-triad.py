import numpy as np
from scipy.io import wavfile

# --- File Parameters ---
duration = 1800.0   # 30 minutes in seconds
sample_rate = 44100  # CD quality sample rate

# --- The Physics Coordinates ---
f_base_triad = np.array([132.0, 423.0, 555.0]) # Al-Si Earth Crust Triad
f_downregulate = 6.0                           # Target Theta/Delta beat (Hz)

# Generate time vector
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

# Initialize stereo channels
left_channel = np.zeros_like(t)
right_channel = np.zeros_like(t)

# --- Synthesize the Multi-Carrier Matrix ---
# We normalize the amplitude to prevent digital clipping when summing the triad
amplitude = 0.3 

for f_carrier in f_base_triad:
    # Left Ear gets the raw physics frequency
    left_channel += amplitude * np.sin(2 * np.pi * f_carrier * t)
    # Right Ear gets the frequency downregulated by our brainwave target
    right_channel += amplitude * np.sin(2 * np.pi * (f_carrier - f_downregulate) * t)

# Combine into a stereo array
stereo_data = np.vstack((left_channel, right_channel)).T

# Convert to 16-bit PCM for WAV export
stereo_data = (stereo_data * 32767).astype(np.int16)

# Export the file
output_filename = "earth_crust_theta_6hz.wav"
wavfile.write(output_filename, sample_rate, stereo_data)

print(f"Success! '{output_filename}' generated with a {f_downregulate}Hz brainwave delta.")