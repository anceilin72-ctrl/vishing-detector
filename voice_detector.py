"""
voice_detector.py
-----------------
Detects whether an audio sample is AI-generated (TTS/synthetic)
or a real human voice using acoustic feature analysis.

How it works:
  - Extracts MFCC, spectral, pitch and harmonic features via librosa
  - Scores each feature against known heuristics for synthetic voice
  - Returns a probability + label (AI / Human / Uncertain)

Install dependencies:
  pip install librosa numpy soundfile
"""

import io
import numpy as np

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

# ── Optional: trained classifier (auto-used if model file exists) ─────────────
try:
    from voice_classifier_trainer import predict_with_trained_model
    TRAINED_MODEL_AVAILABLE = True
except ImportError:
    TRAINED_MODEL_AVAILABLE = False

# ── Pretrained SpeechBrain disabled (torchaudio version conflict) ─────────────
PRETRAINED_AVAILABLE = False


# ---------------------------------------------------------------------------
# Core detector
# ---------------------------------------------------------------------------

def detect_voice_type(audio_bytes: bytes, sr_target: int = 16000) -> dict:
    """
    Analyse raw audio bytes and return a voice-type prediction.

    Returns dict with keys:
        label        – "AI Generated" | "Human" | "Uncertain"
        confidence   – float 0-100
        ai_score     – float 0-100  (higher = more likely AI)
        features     – dict of extracted feature values
        error        – str | None
    """
    # ── Priority 1: Use YOUR trained classifier if model file exists ──────────
    if TRAINED_MODEL_AVAILABLE:
        result = predict_with_trained_model(audio_bytes)
        if result is not None:
            print(f"🎯 Using trained classifier → {result['label']}")
            return result

    # ── Priority 2: Use pretrained SpeechBrain model if installed ─────────────
    if PRETRAINED_AVAILABLE:
        result = detect_with_pretrained(audio_bytes)
        if result is not None and result.get("error") is None:
            print(f"🤖 Using pretrained model → {result['label']}")
            return result

    # ── Priority 3: Heuristic fallback ────────────────────────────────────────
    print("📐 Using heuristic scoring (no trained model found)")

    if not LIBROSA_AVAILABLE:
        return _error_result("librosa is not installed. Run: pip install librosa")

    try:
        y, sr = librosa.load(io.BytesIO(audio_bytes), sr=sr_target, mono=True)
    except Exception as exc:
        return _error_result(f"Could not load audio: {exc}")

    if len(y) < sr * 0.5:
        return _error_result("Audio clip is too short (< 0.5 s).")

    # ── Trim to first 10 seconds — pyin is very slow on long audio ────────────
    max_samples = sr * 10
    if len(y) > max_samples:
        y = y[:max_samples]
        print(f"✂ Audio trimmed to 10s for faster analysis")

    features = _extract_features(y, sr)
    ai_score  = _score_features(features)

    if ai_score >= 65:
        label      = "AI Generated"
        confidence = ai_score
    elif ai_score <= 35:
        label      = "Human"
        confidence = 100 - ai_score
    else:
        label      = "Uncertain"
        confidence = 50 + abs(ai_score - 50)

    return {
        "label":      label,
        "confidence": round(float(confidence), 1),
        "ai_score":   round(float(ai_score),   1),
        "features":   {k: round(float(v), 4) for k, v in features.items()},
        "error":      None,
    }


# ---------------------------------------------------------------------------
# Feature extraction
# ---------------------------------------------------------------------------

def _extract_features(y: np.ndarray, sr: int) -> dict:
    """Return a flat dict of scalar acoustic features."""
    feats = {}

    # --- MFCCs ---
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    feats["mfcc_mean"]     = float(np.mean(mfcc))
    feats["mfcc_std"]      = float(np.std(mfcc))
    feats["mfcc_delta_std"]= float(np.std(librosa.feature.delta(mfcc)))

    # --- Spectral features ---
    spec_cent = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    feats["spectral_centroid_mean"] = float(np.mean(spec_cent))
    feats["spectral_centroid_std"]  = float(np.std(spec_cent))

    spec_bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
    feats["spectral_bw_mean"] = float(np.mean(spec_bw))
    feats["spectral_bw_std"]  = float(np.std(spec_bw))

    spec_flat = librosa.feature.spectral_flatness(y=y)[0]
    feats["spectral_flatness_mean"] = float(np.mean(spec_flat))

    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
    feats["rolloff_mean"] = float(np.mean(rolloff))
    feats["rolloff_std"]  = float(np.std(rolloff))

    # --- Zero crossing rate (measures noisiness) ---
    zcr = librosa.feature.zero_crossing_rate(y)[0]
    feats["zcr_mean"] = float(np.mean(zcr))
    feats["zcr_std"]  = float(np.std(zcr))

    # --- Pitch / F0 regularity (key cue: TTS is very regular) ---
    try:
        f0, voiced_flag, _ = librosa.pyin(
            y, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7"),
            sr=sr, fill_na=np.nan
        )
        voiced_f0 = f0[voiced_flag == 1] if voiced_flag is not None else np.array([])
        if len(voiced_f0) > 4:
            feats["f0_std"]          = float(np.nanstd(voiced_f0))
            feats["f0_range"]        = float(np.nanmax(voiced_f0) - np.nanmin(voiced_f0))
            feats["voiced_fraction"] = float(np.sum(voiced_flag) / len(voiced_flag))
        else:
            # No clear pitch — treat as noisy/human-like
            feats["f0_std"]          = 30.0
            feats["f0_range"]        = 100.0
            feats["voiced_fraction"] = 0.3
    except Exception:
        feats["f0_std"]          = 30.0
        feats["f0_range"]        = 100.0
        feats["voiced_fraction"] = 0.3

    # --- Harmonics-to-Noise Ratio proxy ---
    harmonic, percussive = librosa.effects.hpss(y)
    harmonic_energy   = float(np.mean(harmonic ** 2) + 1e-10)
    percussive_energy = float(np.mean(percussive ** 2) + 1e-10)
    feats["hnr_proxy"] = float(harmonic_energy / (harmonic_energy + percussive_energy))

    # --- RMS energy variability ---
    rms = librosa.feature.rms(y=y)[0]
    feats["rms_std"]  = float(np.std(rms))
    feats["rms_mean"] = float(np.mean(rms))

    # --- Jitter proxy (frame-to-frame pitch micro-variation) ---
    if feats["f0_std"] > 0 and feats.get("voiced_fraction", 0) > 0.1:
        feats["jitter_proxy"] = min(feats["f0_std"] / 50.0, 1.0)
    else:
        feats["jitter_proxy"] = 0.1   # default: slightly human-leaning

    return feats


# ---------------------------------------------------------------------------
# Scoring heuristics
# ---------------------------------------------------------------------------

def _score_features(f: dict) -> float:
    """
    Return an AI probability score 0-100.
    Starts at 30 (lean human). Evidence of synthetic voice pushes score UP.
    Evidence of natural human voice pulls score DOWN.

    Key differences:
      • TTS: unnaturally steady pitch (low F0 std)
      • TTS: over-smoothed spectrum (high spectral flatness)
      • TTS: less dynamic micro-modulation (low MFCC delta std)
      • TTS: hyper-consistent noise floor (low ZCR std)
      • TTS: extremely clean harmonics (very high HNR)
      • Human: natural energy dips from breathing/pauses (high RMS std)
      • Human: pitch micro-jitter and irregularity
    """
    score = 30.0   # lean human by default

    # ── 1. Pitch steadiness ────────────────────────────────────────────────
    f0_std = f.get("f0_std", 30.0)
    if f0_std < 8:
        score += 20      # very flat → strong AI signal
    elif f0_std < 18:
        score += 10
    elif f0_std < 28:
        score += 2
    elif f0_std > 45:
        score -= 10      # very varied → strong human signal
    elif f0_std > 30:
        score -= 5

    # ── 2. Spectral flatness ───────────────────────────────────────────────
    flat = f.get("spectral_flatness_mean", 0.03)
    if flat > 0.10:
        score += 15      # very flat spectrum → AI
    elif flat > 0.07:
        score += 8
    elif flat > 0.04:
        score += 2
    elif flat < 0.015:
        score -= 10      # rich harmonics → human
    elif flat < 0.025:
        score -= 5

    # ── 3. MFCC delta std ─────────────────────────────────────────────────
    mfcc_d = f.get("mfcc_delta_std", 8.0)
    if mfcc_d < 3:
        score += 12
    elif mfcc_d < 6:
        score += 6
    elif mfcc_d < 10:
        score += 1
    elif mfcc_d > 18:
        score -= 10      # very dynamic → human
    elif mfcc_d > 13:
        score -= 5

    # ── 4. ZCR std ────────────────────────────────────────────────────────
    zcr_std = f.get("zcr_std", 0.04)
    if zcr_std < 0.015:
        score += 10
    elif zcr_std < 0.025:
        score += 5
    elif zcr_std > 0.07:
        score -= 7       # noisy/irregular → human
    elif zcr_std > 0.05:
        score -= 3

    # ── 5. HNR proxy ──────────────────────────────────────────────────────
    hnr = f.get("hnr_proxy", 0.75)
    if hnr > 0.95:
        score += 12      # perfectly clean → AI
    elif hnr > 0.90:
        score += 6
    elif hnr > 0.85:
        score += 2
    elif hnr < 0.60:
        score -= 8       # noisy → human
    elif hnr < 0.70:
        score -= 3

    # ── 6. Spectral bandwidth variability ─────────────────────────────────
    bw_std = f.get("spectral_bw_std", 350.0)
    if bw_std < 150:
        score += 8
    elif bw_std < 250:
        score += 3
    elif bw_std > 600:
        score -= 7       # highly variable → human
    elif bw_std > 450:
        score -= 3

    # ── 7. RMS energy variation ───────────────────────────────────────────
    rms_std = f.get("rms_std", 0.03)
    if rms_std < 0.008:
        score += 8       # unnaturally constant volume → AI
    elif rms_std < 0.015:
        score += 4
    elif rms_std > 0.06:
        score -= 7       # natural loudness variation → human
    elif rms_std > 0.04:
        score -= 3

    # ── 8. Jitter proxy ───────────────────────────────────────────────────
    jitter = f.get("jitter_proxy", 0.1)
    if jitter < 0.05:
        score += 8       # too steady → AI
    elif jitter < 0.10:
        score += 3
    elif jitter > 0.40:
        score -= 8       # micro-variation → human
    elif jitter > 0.25:
        score -= 4

    # ── 9. Voiced fraction ────────────────────────────────────────────────
    vf = f.get("voiced_fraction", 0.3)
    if vf > 0.80:
        score += 5       # suspiciously high voiced ratio → AI
    elif vf < 0.20:
        score -= 3       # natural silences → human

    return max(0.0, min(100.0, score))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _error_result(msg: str) -> dict:
    return {
        "label":      "Unknown",
        "confidence": 0.0,
        "ai_score":   0.0,
        "features":   {},
        "error":      msg,
    }