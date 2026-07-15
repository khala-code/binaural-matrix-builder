import numpy as np
from scipy.io import wavfile
import argparse

def generate_decoupled_matrix(beat_freq, meter, bpm, click_gain, duration=600.0, sample_rate=44100):
    """
    Synthesizes a continuous, pristine dual-ear phase-slipped matrix mapped to the 
    geodynamic Al-Si triad, overlaid with an independent, adjustable, smooth metronomic click track.
    """
    f_crystal = np.array([132.0, 423.0, 555.0])
    offset = beat_freq / 2.0
    
    print(f"\n[+] Initializing High-Volume Decoupled Audio Engine...")
    print(f"    - Phantom Center: {f_crystal[0]}Hz | {f_crystal[1]}Hz | {f_crystal[2]}Hz (100% Continuous)")
    print(f"    - Target Beat:    {beat_freq} Hz Intercept")
    print(f"    - Click Layer:    {meter} Meter @ {bpm} BPM (Target Gain: {click_gain})")
    
    # 1. Compute Pristine Continuous Binaural Waves
    total_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, total_samples, endpoint=False)
    left_channel = np.zeros_like(t)
    right_channel = np.zeros_like(t)
    carrier_amplitude = 0.25 # Clean baseline headroom

    for f_center in f_crystal:
        left_channel += carrier_amplitude * np.sin(2 * np.pi * (f_center + offset) * t)
        right_channel += carrier_amplitude * np.sin(2 * np.pi * (f_center - offset) * t)

    # 2. Synthesize a Single "Smooth Click" Transient
    # An 800Hz tone with an ultra-smooth micro-attack and rapid exponential decay
    click_duration = 0.06  # 60 milliseconds
    click_samples = int(sample_rate * click_duration)
    t_click = np.linspace(0, click_duration, click_samples, endpoint=False)
    
    # Smooth S-curve attack (2ms) to eliminate any transient pop
    attack_samples = int(sample_rate * 0.002)
    click_env = np.ones(click_samples)
    click_env[:attack_samples] = np.sin(np.linspace(0, np.pi/2, attack_samples))
    
    # Exponential decay for the remaining tail
    click_env[attack_samples:] = np.exp(-120 * t_click[attack_samples:])
    smooth_click = np.sin(2 * np.pi * 800.0 * t_click) * click_env

    # 3. Construct the Independent Click Track Grid
    click_track = np.zeros(total_samples)
    beats_per_measure = 4 if meter == '4/4' else 3
    samples_per_beat = int(sample_rate * (60.0 / bpm))
    
    total_beats = int(duration * (bpm / 60.0))
    
    for beat_idx in range(total_beats):
        start_sample = beat_idx * samples_per_beat
        end_sample = start_sample + click_samples
        
        # Ensure we don't write past the end of the file array
        if end_sample > total_samples:
            break
            
        # Accent Beat 1 of every measure (downbeat), scale upbeats proportionally
        if beat_idx % beats_per_measure == 0:
            accent_gain = click_gain       # User-specified full volume for primary anchor
        else:
            accent_gain = click_gain * 0.35 # Clear, audible secondary tracking ticks
            
        click_track[start_sample:end_sample] += smooth_click * accent_gain

    # 4. Mix the Decoupled Rhythmic Layer into the Stereo Field
    left_channel += click_track
    right_channel += click_track

    # 5. Prevent Digital Clipping via Global Peak Normalization
    stereo_data = np.vstack((left_channel, right_channel)).T
    max_val = np.max(np.abs(stereo_data))
    if max_val > 1.0:
        stereo_data /= max_val
        
    # Cast to 16-bit PCM for universal hardware compatibility
    stereo_data = (stereo_data * 32767).astype(np.int16)

    meter_str = meter.replace('/', '_')
    output_filename = f"matrix_decoupled_{beat_freq}hz_{meter_str}_{int(bpm)}bpm.wav"
    wavfile.write(output_filename, sample_rate, stereo_data)
    
    print(f"[SUCCESS] High-contrast track successfully compiled: '{output_filename}'\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Decoupled Geodynamic Binaural Matrix Architect (High-Contrast Click Patch)")
    
    # Required Arguments
    parser.add_argument('--beat', type=float, required=True, help="Brainwave frequency in Hz")
    parser.add_argument('--meter', type=str, required=True, choices=['4/4', '3/4'], help="Rhythmic meter ('4/4' or '3/4')")
    
    # Optional Arguments with optimized defaults
    parser.add_argument('--bpm', type=float, default=60.0, help="Tempo baseline in BPM (Default: 60.0)")
    parser.add_argument('--click-gain', type=float, default=0.5, 
                        help="Relative gain limit of the metronome downbeat, scale from 0.0 to 1.0 (Default: 0.5 for high clarity)")
    parser.add_argument('--duration', type=float, default=600.0, help="Runtime in seconds (Default: 600.0)")

    args = parser.parse_args()
    
    generate_decoupled_matrix(
        beat_freq=args.beat,
        meter=args.meter,
        bpm=args.bpm,
        click_gain=args.click_gain,
        duration=args.duration
    )