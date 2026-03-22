"""
debug_test.py
-------------
Run this to find exactly where your pipeline is hanging.

Usage:
    python debug_test.py path/to/your/audio.mp3
"""

import sys
import time
import os

# Fix path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

audio_file = sys.argv[1] if len(sys.argv) > 1 else None

if not audio_file:
    print("Usage: python debug_test.py path/to/audio.mp3")
    sys.exit(1)

print(f"\n🔍 Testing pipeline with: {audio_file}")
print("=" * 50)

# ── Step 1: Audio loading ─────────────────────────────────────────────────────
print("\n[1/5] Loading audio...", end=" ", flush=True)
t = time.time()
try:
    from utils.preprocess import load_audio, normalize_audio
    y, sr = load_audio(audio_file)
    y = normalize_audio(y)
    print(f"✅ Done ({time.time()-t:.1f}s) | shape={y.shape}, sr={sr}")
except Exception as e:
    print(f"❌ FAILED: {e}")
    sys.exit(1)

# ── Step 2: Feature extraction ────────────────────────────────────────────────
print("\n[2/5] Extracting features...", end=" ", flush=True)
t = time.time()
try:
    from utils.feature_extraction import extract_features
    features = extract_features(y, sr)
    print(f"✅ Done ({time.time()-t:.1f}s) | {len(features)} features")
except Exception as e:
    print(f"❌ FAILED: {e}")
    sys.exit(1)

# ── Step 3: Voice authenticity ────────────────────────────────────────────────
print("\n[3/5] Voice authenticity check...", end=" ", flush=True)
t = time.time()
try:
    from models.voice_authenticity import detect_voice_authenticity
    voice_type, confidence = detect_voice_authenticity(features)
    print(f"✅ Done ({time.time()-t:.1f}s) | {voice_type} ({confidence})")
except Exception as e:
    print(f"❌ FAILED: {e}")

# ── Step 4: Speech to text ────────────────────────────────────────────────────
print("\n[4/5] Speech to text (Whisper)...", end=" ", flush=True)
print("\n      ⚠ This may take 1-3 mins on first run...")
t = time.time()
try:
    from utils.speech_to_text import speech_to_text
    text = speech_to_text(audio_file)
    print(f"✅ Done ({time.time()-t:.1f}s) | text='{text[:80]}...'")
except Exception as e:
    print(f"❌ FAILED: {e}")
    text = ""

# ── Step 5: Risk scoring ──────────────────────────────────────────────────────
print("\n[5/5] Risk scoring...", end=" ", flush=True)
t = time.time()
try:
    from models.dummy_model import predict_audio, predict_text
    from utils.keyword_detection import detect_keywords
    from utils.risk_scoring import calculate_risk

    audio_score   = predict_audio(features)
    text_score    = predict_text(text) if text else 0
    keywords      = detect_keywords(text) if text else []
    keyword_score = len(keywords) / 5 if keywords else 0
    risk          = calculate_risk(audio_score, text_score, keyword_score)
    print(f"✅ Done ({time.time()-t:.1f}s) | risk={risk:.1f}%")
except Exception as e:
    print(f"❌ FAILED: {e}")

print("\n" + "=" * 50)
print("✅ Pipeline test complete!")
print("The step that took longest is your bottleneck.")