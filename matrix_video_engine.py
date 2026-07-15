import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import argparse
import sys

try:
    from moviepy import VideoClip, AudioArrayClip
    HAS_MOVIEPY_V2 = True
except ImportError:
    try:
        from moviepy.editor import VideoClip, AudioArrayClip
        HAS_MOVIEPY_V2 = False
    except ImportError:
        print("[ERROR] MoviePy not found. Run: python -m pip install moviepy")
        sys.exit(1)

class TurboMatrixVisualizer:
    def __init__(self, t, left, right, click_track, sample_rate, beat_freq, meter, bpm):
        self.t = t
        self.left = left
        self.right = right
        self.click_track = click_track
        self.sample_rate = sample_rate
        self.beat_freq = beat_freq
        
        self.window_duration = 0.040 
        self.window_samples = int(sample_rate * self.window_duration)
        
        # Build Dark Canvas ONCE and explicitly drop DPI to 80 (960x480 resolution)
        plt.style.use('dark_background')
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(12, 6), dpi=80, facecolor='#0B0C10')
        self.canvas = FigureCanvasAgg(self.fig)
        
        self.fig.suptitle(f"GEODYNAMIC BIOHACKING MATRIX\nCenter: 132 | 423 | 555 Hz  •  Intercept: {beat_freq}Hz  •  Grid: {meter} @ {bpm} BPM", 
                          color='#66FCF1', fontsize=12, fontweight='bold', y=0.96)
        
        # --- Initialize Static Infrastructure Once ---
        self.ax1.set_facecolor('#1F2833')
        self.ax1.set_title("Hemispheric Phase Slip (Oscilloscope)", color='#66FCF1', fontsize=10)
        self.ax1.set_xlabel("Time Window (ms)", color='#C5C6C7')
        self.ax1.grid(True, color='#0B0C10', alpha=0.5)
        
        self.ax2.set_facecolor('#1F2833')
        self.ax2.set_title(f"Quantum Brainwave Intercept ({beat_freq}Hz Orbit)", color='#66FCF1', fontsize=10)
        self.ax2.set_aspect('equal')
        self.ax2.grid(True, color='#0B0C10', alpha=0.5)
        
        # Instantiate persistent line references with empty placeholder arrays
        self.line_left, = self.ax1.plot([], [], color='#66FCF1', lw=1.5, label='Left Channel')
        self.line_right, = self.ax1.plot([], [], color='#45A29E', lw=1.5, label='Right Channel')
        self.line_orbit, = self.ax2.plot([], [], color='#66FCF1', lw=2.0, alpha=0.8)
        
        # Cache tight layout properties to prevent recalculation stalls
        self.fig.tight_layout(rect=[0, 0.03, 1, 0.92])

    def make_frame(self, t_frame):
        center_idx = int(t_frame * self.sample_rate)
        start_idx = max(0, center_idx - self.window_samples // 2)
        end_idx = min(len(self.t), start_idx + self.window_samples)
        
        t_slice = self.t[start_idx:end_idx]
        left_slice = self.left[start_idx:end_idx]
        right_slice = self.right[start_idx:end_idx]
        
        # Audio reactive dynamics calculations
        current_click_amp = self.click_track[center_idx] if center_idx < len(self.click_track) else 0.0
        pulse_scale = 1.0 + (current_click_amp * 2.0)
        line_thickness = 1.5 + (current_click_amp * 8.0)
        
        # --- Update Object Telemetry Instead of Reclearing ---
        t_ms = t_slice * 1000
        self.line_left.set_data(t_ms, left_slice)
        self.line_left.set_linewidth(line_thickness / 2)
        
        self.line_right.set_data(t_ms, right_slice)
        self.line_right.set_linewidth(line_thickness / 2)
        
        self.line_orbit.set_data(left_slice, right_slice)
        self.line_orbit.set_linewidth(line_thickness)
        
        # Modulate boundaries smoothly dynamically without rebuilding axes objects
        limit_ceiling = 1.2 * pulse_scale
        self.ax1.set_xlim(t_ms[0], t_ms[-1])
        self.ax1.set_ylim(-limit_ceiling, limit_ceiling)
        self.ax2.set_xlim(-limit_ceiling, limit_ceiling)
        self.ax2.set_ylim(-limit_ceiling, limit_ceiling)
        
        # Snapshot the pre-existing frame layout
        self.canvas.draw()
        rgba = self.canvas.buffer_rgba()
        return np.asarray(rgba)[..., :3]

def compile_matrix_video(beat_freq, meter, bpm, click_gain, duration, fps, output_filename):
    f_crystal = np.array([132.0, 423.0, 555.0])
    offset = beat_freq / 2.0
    sample_rate = 44100
    
    print(f"\n[+] Booting Optimized Turbo Video Render Engine...")
    total_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, total_samples, endpoint=False)
    left = np.zeros_like(t)
    right = np.zeros_like(t)
    carrier_amplitude = 0.25

    for f_center in f_crystal:
        left += carrier_amplitude * np.sin(2 * np.pi * (f_center + offset) * t)
        right += carrier_amplitude * np.sin(2 * np.pi * (f_center - offset) * t)

    click_duration = 0.06
    click_samples = int(sample_rate * click_duration)
    t_click = np.linspace(0, click_duration, click_samples, endpoint=False)
    attack_samples = int(sample_rate * 0.002)
    click_env = np.ones(click_samples)
    click_env[:attack_samples] = np.sin(np.linspace(0, np.pi/2, attack_samples))
    click_env[attack_samples:] = np.exp(-120 * t_click[attack_samples:])
    smooth_click = np.sin(2 * np.pi * 800.0 * t_click) * click_env

    click_track = np.zeros(total_samples)
    beats_per_measure = 4 if meter == '4/4' else 3
    samples_per_beat = int(sample_rate * (60.0 / bpm))
    total_beats = int(duration * (bpm / 60.0))
    
    for beat_idx in range(total_beats):
        start_sample = beat_idx * samples_per_beat
        end_sample = start_sample + click_samples
        if end_sample > total_samples:
            break
        if beat_idx % beats_per_measure == 0:
            accent_gain = click_gain
        else:
            accent_gain = click_gain * 0.35
        click_track[start_sample:end_sample] += smooth_click * accent_gain

    left += click_track
    right += click_track

    stereo_audio = np.vstack((left, right)).T
    max_val = np.max(np.abs(stereo_audio))
    if max_val > 1.0:
        stereo_audio /= max_val

    # Initialize Optimized Pipeline
    visualizer = TurboMatrixVisualizer(t, left, right, click_track, sample_rate, beat_freq, meter, bpm)
    video_clip = VideoClip(visualizer.make_frame, duration=duration)
    audio_clip = AudioArrayClip(stereo_audio, fps=sample_rate)
    
    if HAS_MOVIEPY_V2:
        video_clip = video_clip.with_audio(audio_clip)
    else:
        video_clip = video_clip.set_audio(audio_clip)
    
    video_clip.write_videofile(
        output_filename, 
        fps=fps, 
        codec='libx264', 
        audio_codec='aac',
        bitrate="1500k",
        preset="ultrafast" # Swapped to maximum compression speed configuration
    )
    
    plt.close(visualizer.fig)
    print(f"\n[SUCCESS] Media Module Exported via Turbo Engine: '{output_filename}'\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Turbo Symmetrical Media Matrix Engine")
    parser.add_argument('--beat', type=float, required=True)
    parser.add_argument('--meter', type=str, required=True, choices=['4/4', '3/4'])
    parser.add_argument('--bpm', type=float, default=60.0)
    parser.add_argument('--click-gain', type=float, default=0.5)
    parser.add_argument('--duration', type=float, default=30.0)
    parser.add_argument('--fps', type=int, default=24)
    parser.add_argument('--output', type=str, default=None)

    args = parser.parse_args()
    if not args.output:
        meter_str = args.meter.replace('/', '_')
        args.output = f"matrix_turbo_{args.beat}hz_{meter_str}_{int(args.bpm)}bpm.mp4"
        
    compile_matrix_video(args.beat, args.meter, args.bpm, args.click_gain, args.duration, args.fps, args.output)