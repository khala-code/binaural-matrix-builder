import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import os
import sys
import json

# --- Version-Aware Defensive Imports for MoviePy ---
try:
    from moviepy import VideoClip, AudioFileClip
    HAS_MOVIEPY_V2 = True
except ImportError:
    try:
        from moviepy.editor import VideoClip, AudioFileClip
        HAS_MOVIEPY_V2 = False
    except ImportError:
        print("[ERROR] MoviePy environment reference could not be resolved.")
        sys.exit(1)

def load_phrase_matrix(json_path="phrase_matrix.json"):
    if not os.path.exists(json_path):
        print(f"[ERROR] Central dataset file '{json_path}' not found.")
        sys.exit(1)
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [(item['english'], item['mandarin']) for item in data]

class PreRenderedVisualizer:
    def __init__(self, t, left, right, click_track, sample_rate, beat_freq, matrix, bpm):
        self.t = t
        self.left = left
        self.right = right
        self.click_track = click_track
        self.sample_rate = sample_rate
        self.beat_freq = beat_freq
        self.matrix = matrix
        self.bpm = bpm
        self.num_phrases = len(matrix)
        
        self.window_duration = 0.040 
        self.window_samples = int(sample_rate * self.window_duration)
        
        # High-Contrast Dark Sci-Fi Canvas Configuration (960x540 16:9 Optimized for X Video)
        plt.style.use('dark_background')
        # --- Inject Cross-Platform CJK Font Engine Fallbacks ---
        plt.rcParams['font.sans-serif'] = [
            'Microsoft YaHei',  # Windows Core
            'SimHei',           # Windows Alternative
            'PingFang SC',      # macOS Clean Modern
            'Heiti SC',         # macOS Classic
            'Noto Sans CJK SC', # Linux Standard
            'WenQuanYi Micro Hei', # Linux Alternative
            'DejaVu Sans'       # Original System Fallback
        ]
        plt.rcParams['axes.unicode_minus'] = False  # Prevents glyph corruption on negative axes
        plt.rcParams['font.size'] = 12
        
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(12, 6.75), dpi=80, facecolor='#0B0C10')
        self.canvas = FigureCanvasAgg(self.fig)
        
        self.fig.suptitle(f"SEMANTIC ENTRAINMENT MATRIX\nCore: 117 | 131 | 248 Hz  •  Intercept: {beat_freq}Hz Theta  •  Clock: {bpm} BPM 4/4", 
                          color='#45A29E', fontsize=11, fontweight='bold', y=0.96)
        
        # Build Static Vector Fields Once
        self.ax1.set_facecolor('#1F2833')
        self.ax1.grid(True, color='#0B0C10', alpha=0.4)
        self.ax1.set_title("Hemispheric Phase Slip", color='#66FCF1', fontsize=10, pad=10)
        
        self.ax2.set_facecolor('#1F2833')
        self.ax2.grid(True, color='#0B0C10', alpha=0.4)
        self.ax2.set_title("Cytoskeletal Vector Lock", color='#66FCF1', fontsize=10, pad=10)
        self.ax2.set_aspect('equal')
        
        # Persistent Line Placeholders
        self.line_left, = self.ax1.plot([], [], color='#66FCF1', lw=1.5)
        self.line_right, = self.ax1.plot([], [], color='#45A29E', lw=1.5)
        self.line_orbit, = self.ax2.plot([], [], color='#66FCF1', lw=2.0, alpha=0.8)
        
        # Persistent Text Elements
        self.txt_display = self.fig.text(0.5, 0.06, "", color='#66FCF1', fontsize=20, 
                                         fontweight='bold', ha='center', va='center',
                                         bbox=dict(facecolor='#1F2833', alpha=0.8, edgecolor='#45A29E', boxstyle='round,pad=0.5'))
        
        self.fig.tight_layout(rect=[0, 0.15, 1, 0.90])

    def make_frame(self, t_frame):
        center_idx = int(t_frame * self.sample_rate)
        start_idx = max(0, center_idx - self.window_samples // 2)
        end_idx = min(len(self.t), start_idx + self.window_samples)
        
        t_slice = self.t[start_idx:end_idx]
        left_slice = self.left[start_idx:end_idx]
        right_slice = self.right[start_idx:end_idx]
        
        current_click_amp = self.click_track[center_idx] if center_idx < len(self.click_track) else 0.0
        pulse_scale = 1.0 + (current_click_amp * 1.5)
        line_thickness = 1.5 + (current_click_amp * 6.0)
        
        t_ms = t_slice * 1000
        self.line_left.set_data(t_ms, left_slice)
        self.line_left.set_linewidth(line_thickness / 2)
        self.line_right.set_data(t_ms, right_slice)
        self.line_right.set_linewidth(line_thickness / 2)
        
        self.line_orbit.set_data(left_slice, right_slice)
        self.line_orbit.set_linewidth(line_thickness)
        
        limit_ceiling = 1.2 * pulse_scale
        self.ax1.set_xlim(t_ms[0], t_ms[-1])
        self.ax1.set_ylim(-limit_ceiling, limit_ceiling)
        self.ax2.set_xlim(-limit_ceiling, limit_ceiling)
        self.ax2.set_ylim(-limit_ceiling, limit_ceiling)
        
        # Real-Time Text Selection Matrix
        measure_duration = 4.0
        current_measure = int(t_frame // measure_duration)
        t_measure = t_frame % measure_duration
        phrase_idx = current_measure % self.num_phrases
        
        en_text, zh_text = self.matrix[phrase_idx]
        
        if 0.0 <= t_measure < 1.0:
            self.txt_display.set_text(f"ENG ANCHOR:  {en_text.upper()}")
            self.txt_display.set_visible(True)
            self.txt_display.get_bbox_patch().set_edgecolor('#66FCF1')  # Fixed method call
            self.txt_display.set_color('#66FCF1')
        elif 1.0 <= t_measure < 2.0:
            self.txt_display.set_text(f"ENG ANCHOR:  {en_text.upper()}")
            self.txt_display.get_bbox_patch().set_edgecolor('#45A29E')  # Fixed method call
            self.txt_display.set_color('#45A29E')
            self.txt_display.set_visible(True)
        elif 2.0 <= t_measure < 3.0:
            self.txt_display.set_text(f"TARGET MANIFEST:  {zh_text}")
            self.txt_display.get_bbox_patch().set_edgecolor('#66FCF1')  # Fixed method call
            self.txt_display.set_color('#66FCF1')
            self.txt_display.set_visible(True)
        else:
            self.txt_display.set_visible(False)
            
        self.canvas.draw()
        rgba = self.canvas.buffer_rgba()
        return np.asarray(rgba)[..., :3]

def multiplex_existing_track(audio_path="semantic_entrainment_production.wav", json_path="phrase_matrix.json", bpm=60.0, beat_freq=6.0, fps=24):
    if not os.path.exists(audio_path):
        print(f"[ERROR] Target track file '{audio_path}' not found in current directory.")
        sys.exit(1)
        
    print(f"[+] Reading pre-rendered audio source track: '{audio_path}'...")
    sample_rate, data = wavfile.read(audio_path)
    
    # Cast to normalized floating point array
    if data.dtype == np.int16: data = data / 32768.0
    elif data.dtype == np.int32: data = data / 2147483648.0
    
    # Split audio bus fields
    left_channel = data[:, 0]
    right_channel = data[:, 1]
    
    total_samples = len(data)
    duration = total_samples / sample_rate
    
    # Reconstruct the timing click grid solely for driving the visual dashboard pulses
    print("[+] Re-calculating visual synchronization grid components...")
    click_track = np.zeros(total_samples)
    samples_per_beat = int(sample_rate * (60.0 / bpm))
    click_duration = 0.05
    click_samples = int(sample_rate * click_duration)
    t_click = np.linspace(0, click_duration, click_samples, endpoint=False)
    smooth_click = np.exp(-150 * t_click)
    
    total_beats = int(duration * (bpm / 60.0))
    for b in range(total_beats):
        start_idx = b * samples_per_beat
        end_idx = start_idx + click_samples
        if end_idx > total_samples: break
        click_track[start_idx:end_idx] += smooth_click
        
    matrix = load_phrase_matrix(json_path)
    t = np.linspace(0, duration, total_samples, endpoint=False)
    
    print(f"\n[+] Processing Multimedia Multiplexer Pipeline...")
    print(f"    - Track Duration:  {duration:.1f} seconds mapped directly from audio file")
    print(f"    - Render Settings: {fps} FPS | Turbo Object Persistence Mode")
    
    visualizer = PreRenderedVisualizer(t, left_channel, right_channel, click_track, sample_rate, beat_freq, matrix, bpm)
    
    # Generate visual streams frame-by-frame
    video_clip = VideoClip(visualizer.make_frame, duration=duration)
    
    # Import the original audio file asset directly without re-rendering anything
    audio_clip = AudioFileClip(audio_path)
    
    if HAS_MOVIEPY_V2:
        video_clip = video_clip.with_audio(audio_clip)
    else:
        video_clip = video_clip.set_audio(audio_clip)
        
    output_filename = "semantic_entrainment_final.mp4"
    video_clip.write_videofile(
        output_filename, 
        fps=fps, 
        codec='libx264', 
        audio_codec='aac',
        bitrate="1800k",
        preset="ultrafast"
    )
    
    plt.close(visualizer.fig)
    print(f"\n[SUCCESS] Multimedia Master Asset Exported: '{output_filename}'\n")

if __name__ == "__main__":
    multiplex_existing_track()