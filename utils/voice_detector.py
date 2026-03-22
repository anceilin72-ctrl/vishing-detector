"""
voice_detector.py — AI vs Human voice detector (fast version)
"""
import io
import numpy as np

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

try:
    from voice_classifier_trainer import predict_with_trained_model
    TRAINED_MODEL_AVAILABLE = True
except ImportError:
    TRAINED_MODEL_AVAILABLE = False

PRETRAINED_AVAILABLE = False


def detect_voice_type(audio_bytes: bytes, sr_target: int = 16000) -> dict:
    # ── Priority 1: Trained classifier ───────────────────────────────────────
    if TRAINED_MODEL_AVAILABLE:
        result = predict_with_trained_model(audio_bytes)
        if result is not None:
            print(f"🎯 Trained classifier → {result['label']}")
            return result

    # ── Priority 2: Heuristic fallback ───────────────────────────────────────
    if not LIBROSA_AVAILABLE:
        return _error("librosa not installed")

    try:
        y, sr = librosa.load(io.BytesIO(audio_bytes), sr=sr_target, mono=True)
    except Exception as e:
        return _error(f"Could not load audio: {e}")

    if len(y) < sr * 0.5:
        return _error("Audio too short")

    # Trim to 5s max for speed
    y = y[:sr * 5] if len(y) > sr * 5 else y

    features = _extract_features(y, sr)
    ai_score = _score_features(features)

    if ai_score >= 65:
        label, confidence = "AI Generated", ai_score
    elif ai_score <= 35:
        label, confidence = "Human", 100 - ai_score
    else:
        label, confidence = "Uncertain", 50 + abs(ai_score - 50)

    return {
        "label":      label,
        "confidence": round(float(confidence), 1),
        "ai_score":   round(float(ai_score), 1),
        "features":   {},
        "error":      None,
    }


def _extract_features(y: np.ndarray, sr: int) -> dict:
    feats = {}

    # MFCCs
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    feats["mfcc_mean"]      = float(np.mean(mfcc))
    feats["mfcc_std"]       = float(np.std(mfcc))
    feats["mfcc_delta_std"] = float(np.std(librosa.feature.delta(mfcc)))

    # Spectral
    feats["spectral_centroid_mean"] = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
    feats["spectral_centroid_std"]  = float(np.std(librosa.feature.spectral_centroid(y=y, sr=sr)))
    spec_bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
    feats["spectral_bw_mean"]       = float(np.mean(spec_bw))
    feats["spectral_bw_std"]        = float(np.std(spec_bw))
    feats["spectral_flatness_mean"] = float(np.mean(librosa.feature.spectral_flatness(y=y)))
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
    feats["rolloff_mean"] = float(np.mean(rolloff))
    feats["rolloff_std"]  = float(np.std(rolloff))

    # ZCR
    zcr = librosa.feature.zero_crossing_rate(y)[0]
    feats["zcr_mean"] = float(np.mean(zcr))
    feats["zcr_std"]  = float(np.std(zcr))

    # Pitch — use fast yin on 3s only (10x faster than pyin)
    try:
        y_short  = y[:sr * 3] if len(y) > sr * 3 else y
        f0       = librosa.yin(y_short, fmin=librosa.note_to_hz("C2"),
                               fmax=librosa.note_to_hz("C7"), sr=sr)
        f0_voiced = f0[f0 > 0]
        if len(f0_voiced) > 4:
            feats["f0_std"]          = float(np.std(f0_voiced))
            feats["f0_range"]        = float(np.max(f0_voiced) - np.min(f0_voiced))
            feats["voiced_fraction"] = float(len(f0_voiced) / len(f0))
        else:
            feats["f0_std"], feats["f0_range"], feats["voiced_fraction"] = 30.0, 100.0, 0.3
    except Exception:
        feats["f0_std"], feats["f0_range"], feats["voiced_fraction"] = 30.0, 100.0, 0.3

    # HNR proxy — fast spectral contrast (replaces slow hpss)
    try:
        contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        hnr = float(np.mean(contrast) / 50.0)
        feats["hnr_proxy"] = min(1.0, max(0.0, hnr))
    except Exception:
        feats["hnr_proxy"] = 0.75

    # RMS
    rms = librosa.feature.rms(y=y)[0]
    feats["rms_std"]  = float(np.std(rms))
    feats["rms_mean"] = float(np.mean(rms))

    # Jitter proxy
    feats["jitter_proxy"] = min(feats["f0_std"] / 50.0, 1.0) if feats["f0_std"] > 0 else 0.1

    return feats


def _score_features(f: dict) -> float:
    score = 30.0

    f0_std = f.get("f0_std", 30.0)
    if f0_std < 8:     score += 20
    elif f0_std < 18:  score += 10
    elif f0_std < 28:  score += 2
    elif f0_std > 45:  score -= 10
    elif f0_std > 30:  score -= 5

    flat = f.get("spectral_flatness_mean", 0.03)
    if flat > 0.10:    score += 15
    elif flat > 0.07:  score += 8
    elif flat > 0.04:  score += 2
    elif flat < 0.015: score -= 10
    elif flat < 0.025: score -= 5

    mfcc_d = f.get("mfcc_delta_std", 8.0)
    if mfcc_d < 3:     score += 12
    elif mfcc_d < 6:   score += 6
    elif mfcc_d < 10:  score += 1
    elif mfcc_d > 18:  score -= 10
    elif mfcc_d > 13:  score -= 5

    zcr_std = f.get("zcr_std", 0.04)
    if zcr_std < 0.015:  score += 10
    elif zcr_std < 0.025: score += 5
    elif zcr_std > 0.07:  score -= 7
    elif zcr_std > 0.05:  score -= 3

    hnr = f.get("hnr_proxy", 0.75)
    if hnr > 0.95:    score += 12
    elif hnr > 0.90:  score += 6
    elif hnr > 0.85:  score += 2
    elif hnr < 0.60:  score -= 8
    elif hnr < 0.70:  score -= 3

    bw_std = f.get("spectral_bw_std", 350.0)
    if bw_std < 150:   score += 8
    elif bw_std < 250: score += 3
    elif bw_std > 600: score -= 7
    elif bw_std > 450: score -= 3

    rms_std = f.get("rms_std", 0.03)
    if rms_std < 0.008:  score += 8
    elif rms_std < 0.015: score += 4
    elif rms_std > 0.06:  score -= 7
    elif rms_std > 0.04:  score -= 3

    jitter = f.get("jitter_proxy", 0.1)
    if jitter < 0.05:   score += 8
    elif jitter < 0.10: score += 3
    elif jitter > 0.40: score -= 8
    elif jitter > 0.25: score -= 4

    vf = f.get("voiced_fraction", 0.3)
    if vf > 0.80:  score += 5
    elif vf < 0.20: score -= 3

    return max(0.0, min(100.0, score))


def _error(msg: str) -> dict:
    return {"label": "Unknown", "confidence": 0.0, "ai_score": 0.0, "features": {}, "error": msg}