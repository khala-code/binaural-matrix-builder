import os
import sys
import json
from gtts import gTTS

# --- Version-Aware Defensive Imports for MoviePy ---
try:
    # Modern MoviePy v2.x layout
    from moviepy import AudioFileClip
except ImportError:
    try:
        # Legacy MoviePy v1.x layout
        from moviepy.editor import AudioFileClip
    except ImportError:
        print("[ERROR] MoviePy environment reference could not be resolved.")
        print("        Please ensure your active terminal environment has moviepy installed.")
        sys.exit(1)

def load_phrase_matrix(json_path="phrase_matrix.json"):
    """Loads the centralized phrase dataset from JSON and converts it to list format."""
    if not os.path.exists(json_path):
        print(f"[ERROR] Central dataset file '{json_path}' not found.")
        sys.exit(1)
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [(item['english'], item['mandarin']) for item in data]

def build_asset_directory(asset_dir="semantic_assets"):
    """Ensures the production asset directory exists safely on disk."""
    if not os.path.exists(asset_dir):
        os.makedirs(asset_dir)
        print(f"[+] Created local asset framework directory: '{asset_dir}/'")
    else:
        print(f"[+] Target production directory '{asset_dir}/' verified active.")

def generate_and_convert_tts(json_path="phrase_matrix.json", asset_dir="semantic_assets"):
    matrix = load_phrase_matrix(json_path)
    build_asset_directory(asset_dir)
    total_pairs = len(matrix)
    
    print(f"\n[+] Initializing Automated Vocal Pipeline Asset Compiler...")
    print(f"    - Extraction Source: Google Text-to-Speech Engine")
    print(f"    - Target Configuration: 44100Hz | 16-Bit Signed Integer PCM WAV")
    print(f"    - Audio Processing Engine: MoviePy Internal Multiplexer Binary\n")
    
    for idx, (en_text, zh_text) in enumerate(matrix):
        print(f"[{idx+1:02d}/{total_pairs:02d}] Synthesizing Pair: \"{en_text}\" <-> \"{zh_text}\"")
        
        # Define short-term scratch storage filenames
        temp_en_mp3 = "scratch_en.mp3"
        temp_zh_mp3 = "scratch_zh.mp3"
        
        # Define absolute final target production pathing matching the mixer expectations
        out_en_wav = os.path.join(asset_dir, f"en_{idx}.wav")
        out_zh_wav = os.path.join(asset_dir, f"zh_{idx}.wav")
        
        # 1. Ping Google TTS servers and grab the raw phrase audio layers
        tts_en = gTTS(text=en_text, lang='en', slow=False)
        tts_en.save(temp_en_mp3)
        
        tts_zh = gTTS(text=zh_text, lang='zh-CN', slow=False)
        tts_zh.save(temp_zh_mp3)
        
        # 2. Open stream clips and enforce absolute WAV parameters using the moviepy sub-layer
        # Process the English Anchor Token
        clip_en = AudioFileClip(temp_en_mp3)
        clip_en.write_audiofile(out_en_wav, fps=44100, nbytes=2, codec='pcm_s16le', logger=None)
        clip_en.close()
        
        # Process the Mandarin Target Vector Token
        clip_zh = AudioFileClip(temp_zh_mp3)
        clip_zh.write_audiofile(out_zh_wav, fps=44100, nbytes=2, codec='pcm_s16le', logger=None)
        clip_zh.close()
        
        # 3. Secure File Cleanup: Instantly wipe scratch files to leave no artifacts
        os.remove(temp_en_mp3)
        os.remove(temp_zh_mp3)
        
    print(f"\n[SUCCESS] Custom Linguistic Workspace Built! All {total_pairs * 2} semantic tokens loaded.")
    print(f"          Ready to execute your master 'matrix_production_compiler.py' download track.\n")

if __name__ == "__main__":
    generate_and_convert_tts()