import numpy as np
from scipy.io import wavfile
import os
import sys
import json

def load_phrase_matrix(json_path="phrase_matrix.json"):
    """Loads the centralized phrase dataset from JSON and converts it to list format."""
    if not os.path.exists(json_path):
        print(f"[ERROR] Central dataset file '{json_path}' not found.")
        sys.exit(1)
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [(item['english'], item['mandarin']) for item in data]

def load_production_tokens(matrix, asset_dir, target_sr=44100):
    """
    Reads real English and Mandarin WAV assets from the disk, normalizes their volume,
    and forces them into exact 1-second mono memory blocks.
    """
    print(f"[+] Scanning '{asset_dir}' for production voice payloads...")
    en_arrays = []
    zh_arrays = []
    max_samples = int(target_sr * 1.0) # 1-second maximum boundary
    
    for idx in range(len(matrix)):
        en_path = os.path.join(asset_dir, f"en_{idx}.wav")
        zh_path = os.path.join(asset_dir, f"zh_{idx}.wav")
        
        # Defensive check for file integrity
        if not os.path.exists(en_path) or not os.path.exists(zh_path):
            print(f"[ERROR] Missing asset links at index {idx}.")
            print(f"        Ensure '{en_path}' and '{zh_path}' exist.")
            sys.exit(1)
            
        # Parse and process each language token pair
        for path, array_destination in [(en_path, en_arrays), (zh_path, zh_arrays)]:
            sr, data = wavfile.read(path)
            
            # Cast to normalized floating point
            if data.dtype == np.int16:
                data = data / 32768.0
            elif data.dtype == np.int32:
                data = data / 2147483648.0
                
            # Collapse to mono if file is stereo
            if len(data.shape) > 1:
                data = np.mean(data, axis=1)
                
            # Re-sample timeline if sample rate matches incorrectly
            if sr != target_sr:
                indices = np.round(np.linspace(0, len(data) - 1, int(target_sr * (len(data) / sr)))).astype(int)
                data = data[indices]
                
            # Enforce 1-second crop or pad with digital silence
            if len(data) > max_samples:
                data = data[:max_samples]
            else:
                data = np.pad(data, (0, max_samples - len(data)), 'constant')
                
            # Peak value volume normalization step
            data = data / (np.max(np.abs(data)) + 1e-5)
            array_destination.append(data)
            
    return en_arrays, zh_arrays

def compile_bulk_vector_dock(json_path="phrase_matrix.json", asset_dir="semantic_assets", repetitions=3, bpm=60.0, beat_freq=6.0):
    sample_rate = 44100
    f_crystal = np.array([117.0, 131.0, 248.0])
    offset = beat_freq / 2.0

    matrix = load_phrase_matrix(json_path)
    # Ingest production WAV files
    en_tokens, zh_tokens = load_production_tokens(matrix, asset_dir, sample_rate)
    
    num_phrases = len(matrix)
    samples_per_beat = int(sample_rate * (60.0 / bpm))
    samples_per_measure = samples_per_beat * 4 
    
    total_measures = num_phrases * repetitions
    total_samples = samples_per_measure * total_measures
    duration = total_samples / sample_rate
    
    print(f"\n[+] Compiling Production Semantic Entrainment Matrix...")
    print(f"    - Temporal Clock: {beat_freq}Hz Theta @ {bpm} BPM 4/4")
    print(f"    - Output Runtime: {duration:.1f} seconds total audio duration")
    
    t = np.linspace(0, duration, total_samples, endpoint=False)
    left_channel = np.zeros_like(t)
    right_channel = np.zeros_like(t)
    carrier_amp = 0.20

    # 1. Synthesize Phase-Locked Microtubule Carrier Base
    for f_center in f_crystal:
        left_channel += carrier_amp * np.sin(2 * np.pi * (f_center + offset) * t)
        right_channel += carrier_amp * np.sin(2 * np.pi * (f_center - offset) * t)

    # 2. Synthesize Metronome Tracking Grid
    click_duration = 0.05
    click_samples = int(sample_rate * click_duration)
    t_click = np.linspace(0, click_duration, click_samples, endpoint=False)
    smooth_click = np.sin(2 * np.pi * 900.0 * t_click) * np.exp(-150 * t_click)
    
    click_track = np.zeros(total_samples)
    for b in range(total_measures * 4):
        start_idx = b * samples_per_beat
        end_idx = start_idx + click_samples
        if end_idx > total_samples: break
        gain = 0.12 if b % 4 == 0 else 0.03
        click_track[start_idx:end_idx] += smooth_click * gain

    # 3. Interleave Real Spoken Language Vectors
    semantic_track = np.zeros(total_samples)
    current_measure = 0
    
    for rep in range(repetitions):
        for phrase_idx in range(num_phrases):
            measure_start = current_measure * samples_per_measure
            
            # Beat 1: High-Gain Native English Anchor
            b1_start = measure_start
            b1_end = b1_start + sample_rate
            semantic_track[b1_start:b1_end] += en_tokens[phrase_idx] * 0.3
            
            # Beat 3: Sub-Threshold Masked Mandarin Target Vector
            b3_start = measure_start + (samples_per_beat * 2)
            b3_end = b3_start + sample_rate
            semantic_track[b3_start:b3_end] += zh_tokens[phrase_idx] * 0.1
            
            current_measure += 1

    # Final Audio Multiplexing
    left_channel += click_track + semantic_track
    right_channel += click_track + semantic_track
    
    stereo_out = np.vstack((left_channel, right_channel)).T
    max_peak = np.max(np.abs(stereo_out))
    if max_peak > 1.0:
        stereo_out /= max_peak
        
    output_filename = "semantic_entrainment_production.wav"
    wavfile.write(output_filename, sample_rate, (stereo_out * 32767).astype(np.int16))
    print(f"\n[SUCCESS] Production Matrix compiled as: '{output_filename}'\n")

if __name__ == "__main__":
    compile_bulk_vector_dock(json_path="phrase_matrix.json", asset_dir="semantic_assets", repetitions=3, bpm=60.0, beat_freq=6.0)