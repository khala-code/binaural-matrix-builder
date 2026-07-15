import numpy as np
from scipy.io import wavfile
import argparse

def generate_rhythmic_matrix(beat_freq, meter, bpm, duration=600.0, sample_rate=44100):
    """
    Synthesizes a dual-ear phase-slipped matrix mapped to the geodynamic Al-Si triad,
    modulated by a click-free, anti-aliased rhythmic macro-envelope.
    """
    # Core constants: The Earth-field lithospheric crystal
    f_crystal = np.array([132.0, 423.0, 555.0])
    offset = beat_freq / 2.0
    
    print(f"\n[+] Initializing Patched Audio Synthesis Engine...")
    print(f"    - Target Phantom Center: {f_crystal[0]}Hz | {f_crystal[1]}Hz | {f_crystal[2]}Hz")
    print(f"    - Downregulation Target: {beat_freq} Hz Intercept")
    print(f"    - Left Ear Matrix:       {f_crystal + offset} Hz")
    print(f"    - Right Ear Matrix:      {f_crystal - offset} Hz")
    print(f"    - Rhythmic Grid:         {meter} Meter @ {bpm} BPM (De-clicked)")
    
    # 1. Compute Base Audio Vectors
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    left_channel = np.zeros_like(t)
    right_channel = np.zeros_like(t)
    amplitude = 0.3  # Headroom ceiling to prevent digital summation clipping

    for f_center in f_crystal:
        left_channel += amplitude * np.sin(2 * np.pi * (f_center + offset) * t)
        right_channel += amplitude * np.sin(2 * np.pi * (f_center - offset) * t)

    # 2. Parse Meter and Construct Click-Free Macro-Envelope
    beats_per_measure = 4 if meter == '4/4' else 3
    samples_per_beat = int(sample_rate * (60.0 / bpm))
    samples_per_measure = samples_per_beat * beats_per_measure
    
    measure_env = np.zeros(samples_per_measure)

    # De-clicking Window Parameters (15ms smoothing ramps)
    fade_time = 0.015  
    attack_samples = int(sample_rate * fade_time)
    decay_samples = samples_per_beat - attack_samples

    # Smooth S-Curve Attack (quarter-sine wave interpolation)
    attack_curve = np.sin(np.linspace(0, np.pi / 2, attack_samples))

    # Exponential Decay Curve
    t_decay = np.linspace(0, decay_samples / sample_rate, decay_samples, endpoint=False)
    decay_curve = np.exp(-5 * t_decay)

    # Smooth Fade-out window at the absolute tail of the beat to prevent frame-boundary friction
    fade_out_samples = min(int(sample_rate * fade_time), len(decay_curve))
    fade_out = np.cos(np.linspace(0, np.pi / 2, fade_out_samples))
    decay_curve[-fade_out_samples:] *= fade_out

    # Seamlessly stitch the click-free beat envelope together
    beat_pulse = np.concatenate((attack_curve, decay_curve))

    for beat in range(beats_per_measure):
        start_idx = beat * samples_per_beat
        end_idx = start_idx + samples_per_beat
        
        # Heavy downbeat accent on Beat 1, softer baseline pulses on remaining upbeats
        accent = 1.0 if beat == 0 else 0.4
        measure_env[start_idx:end_idx] = beat_pulse * accent

    # Keep a 20% volume floor so the frequencies blend smoothly without total silence gaps
    baseline_floor = 0.2
    measure_env = baseline_floor + (1.0 - baseline_floor) * measure_env

    # 3. Tile Envelope Across Timeline Matrix
    total_samples = len(t)
    repeats_needed = int(np.ceil(total_samples / samples_per_measure))
    full_envelope = np.tile(measure_env, repeats_needed)[:total_samples]

    # Apply structural envelope to both channels
    left_channel *= full_envelope
    right_channel *= full_envelope

    # 4. Compile Array Interleaving & Export 16-bit PCM WAV
    stereo_data = np.vstack((left_channel, right_channel)).T
    stereo_data = (stereo_data * 32767).astype(np.int16)

    meter_str = meter.replace('/', '_')
    output_filename = f"matrix_patched_{beat_freq}hz_{meter_str}_{int(bpm)}bpm.wav"
    wavfile.write(output_filename, sample_rate, stereo_data)
    
    print(f"[SUCCESS] Patched wetware file compiled: '{output_filename}'\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Patched Geodynamic Symmetrical Brainwave Matrix Architect")
    
    parser.add_argument('--beat', type=float, required=True, help="Brainwave frequency in Hz")
    parser.add_argument('--meter', type=str, required=True, choices=['4/4', '3/4'], help="Rhythmic meter ('4/4' or '3/4')")
    parser.add_argument('--bpm', type=float, default=60.0, help="Tempo baseline in BPM (Default: 60.0)")
    parser.add_argument('--duration', type=float, default=600.0, help="Runtime in seconds (Default: 600.0)")

    args = parser.parse_args()
    
    generate_rhythmic_matrix(
        beat_freq=args.beat,
        meter=args.meter,
        bpm=args.bpm,
        duration=args.duration
    )