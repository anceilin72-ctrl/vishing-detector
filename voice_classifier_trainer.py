"""
voice_classifier_trainer.py
----------------------------
A trainable Random Forest classifier that learns from YOUR labeled audio samples.
Works with as few as 10 samples — improves as you add more.

Workflow:
    1. Collect audio samples (use label_audio.py)
    2. Run: python voice_classifier_trainer.py --train
    3. The model is saved to models/voice_classifier.pkl
    4. voice_detector.py will auto-use it if present

Install:
    pip install librosa scikit-learn numpy joblib soundfile
"""

import os
import io
import json
import argparse
import numpy as np

try:
    import librosa
    LIBROSA_OK = True
except ImportError:
    LIBROSA_OK = False

try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import cross_val_score, StratifiedKFold
    from sklearn.pipeline import Pipeline
    from sklearn.metrics import classification_report
    import joblib
    SKLEARN_OK = True
except ImportError:
    SKLEARN_OK = False


SAMPLES_DIR  = "training_data"          # where labeled audio lives
MODEL_PATH   = "models/voice_classifier.pkl"
LABELS_FILE  = os.path.join(SAMPLES_DIR, "labels.json")


# ── Feature extraction (same logic as voice_detector.py) ─────────────────────

def extract_features_flat(audio_bytes: bytes, sr_target: int = 16000) -> np.ndarray | None:
    """Extract a flat feature vector from raw audio bytes."""
    if not LIBROSA_OK:
        print("❌ librosa not installed")
        return None
    try:
        y, sr = librosa.load(io.BytesIO(audio_bytes), sr=sr_target, mono=True)
    except Exception as e:
        print(f"  ⚠ Could not load: {e}")
        return None

    if len(y) < sr * 0.5:
        print("  ⚠ Too short, skipping")
        return None

    feats = []

    # MFCCs (mean + std for each of 13 coefficients = 26 values)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    feats.extend(np.mean(mfcc, axis=1).tolist())
    feats.extend(np.std(mfcc, axis=1).tolist())

    # MFCC deltas
    mfcc_delta = librosa.feature.delta(mfcc)
    feats.append(float(np.mean(mfcc_delta)))
    feats.append(float(np.std(mfcc_delta)))

    # Spectral features
    spec_cent = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    feats.append(float(np.mean(spec_cent)))
    feats.append(float(np.std(spec_cent)))

    spec_bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
    feats.append(float(np.mean(spec_bw)))
    feats.append(float(np.std(spec_bw)))

    spec_flat = librosa.feature.spectral_flatness(y=y)[0]
    feats.append(float(np.mean(spec_flat)))
    feats.append(float(np.std(spec_flat)))

    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
    feats.append(float(np.mean(rolloff)))
    feats.append(float(np.std(rolloff)))

    # ZCR
    zcr = librosa.feature.zero_crossing_rate(y)[0]
    feats.append(float(np.mean(zcr)))
    feats.append(float(np.std(zcr)))

    # Pitch
    try:
        f0, voiced_flag, _ = librosa.pyin(
            y, fmin=librosa.note_to_hz("C2"),
            fmax=librosa.note_to_hz("C7"), sr=sr, fill_na=np.nan
        )
        voiced_f0 = f0[voiced_flag == 1] if voiced_flag is not None else np.array([])
        if len(voiced_f0) > 4:
            feats.append(float(np.nanmean(voiced_f0)))
            feats.append(float(np.nanstd(voiced_f0)))
            feats.append(float(np.nanmax(voiced_f0) - np.nanmin(voiced_f0)))
            feats.append(float(np.sum(voiced_flag) / len(voiced_flag)))
        else:
            feats.extend([150.0, 30.0, 100.0, 0.3])
    except Exception:
        feats.extend([150.0, 30.0, 100.0, 0.3])

    # HNR proxy
    harmonic, percussive = librosa.effects.hpss(y)
    h_energy = float(np.mean(harmonic ** 2) + 1e-10)
    p_energy = float(np.mean(percussive ** 2) + 1e-10)
    feats.append(h_energy / (h_energy + p_energy))

    # RMS
    rms = librosa.feature.rms(y=y)[0]
    feats.append(float(np.mean(rms)))
    feats.append(float(np.std(rms)))

    # Chroma
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    feats.append(float(np.mean(chroma)))
    feats.append(float(np.std(chroma)))

    return np.array(feats, dtype=np.float32)


# ── Training ──────────────────────────────────────────────────────────────────

def train():
    if not SKLEARN_OK:
        print("❌ scikit-learn not installed. Run: pip install scikit-learn joblib")
        return

    if not os.path.exists(LABELS_FILE):
        print(f"❌ No labels file found at {LABELS_FILE}")
        print("   Run label_audio.py first to label your samples.")
        return

    with open(LABELS_FILE) as f:
        labels_map = json.load(f)   # { "filename.mp3": "human" | "ai" }

    print(f"📂 Found {len(labels_map)} labeled samples")

    X, y = [], []
    for filename, label in labels_map.items():
        filepath = os.path.join(SAMPLES_DIR, filename)
        if not os.path.exists(filepath):
            print(f"  ⚠ Missing file: {filepath}")
            continue
        with open(filepath, "rb") as f:
            audio_bytes = f.read()
        features = extract_features_flat(audio_bytes)
        if features is not None:
            X.append(features)
            y.append(1 if label == "ai" else 0)
            print(f"  ✅ {filename} → {label}")

    if len(X) < 4:
        print(f"❌ Need at least 4 samples to train (have {len(X)}). Add more labeled audio.")
        return

    X = np.array(X)
    y = np.array(y)

    n_ai    = sum(y == 1)
    n_human = sum(y == 0)
    print(f"\n📊 Dataset: {n_human} human, {n_ai} AI samples")

    # ── Build pipeline ────────────────────────────────────────────────────────
    # Use GradientBoosting for small datasets (handles imbalance better)
    if len(X) < 20:
        clf = GradientBoostingClassifier(
            n_estimators=100, max_depth=3,
            learning_rate=0.1, random_state=42
        )
        print("🌱 Using GradientBoosting (best for small datasets)")
    else:
        clf = RandomForestClassifier(
            n_estimators=200, max_depth=None,
            class_weight="balanced", random_state=42, n_jobs=-1
        )
        print("🌳 Using RandomForest")

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf",    clf),
    ])

    # ── Cross-validation (only if enough samples) ─────────────────────────────
    if len(X) >= 6:
        cv = StratifiedKFold(n_splits=min(3, len(X) // 2), shuffle=True, random_state=42)
        scores = cross_val_score(pipeline, X, y, cv=cv, scoring="accuracy")
        print(f"\n📈 Cross-validation accuracy: {scores.mean():.1%} ± {scores.std():.1%}")
    else:
        print(f"\n⚠ Only {len(X)} samples — skipping cross-validation (need 6+)")

    # ── Final fit on all data ─────────────────────────────────────────────────
    pipeline.fit(X, y)
    print("\n✅ Model trained on all samples")

    # Save
    os.makedirs("models", exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"💾 Model saved to {MODEL_PATH}")
    print("\n🚀 voice_detector.py will now use this trained model automatically!")


# ── Inference (called by voice_detector.py) ───────────────────────────────────

def predict_with_trained_model(audio_bytes: bytes) -> dict | None:
    """
    Returns prediction dict if trained model exists, else None
    (so voice_detector.py can fall back to heuristics).
    """
    if not os.path.exists(MODEL_PATH):
        return None   # no trained model yet
    if not SKLEARN_OK:
        return None

    try:
        pipeline = joblib.load(MODEL_PATH)
    except Exception as e:
        print(f"⚠ Could not load classifier: {e}")
        return None

    features = extract_features_flat(audio_bytes)
    if features is None:
        return None

    features = features.reshape(1, -1)
    proba    = pipeline.predict_proba(features)[0]   # [P(human), P(ai)]
    ai_prob  = float(proba[1]) * 100
    label    = "AI Generated" if ai_prob >= 55 else "Human"
    confidence = ai_prob if ai_prob >= 55 else 100 - ai_prob

    return {
        "label":      label,
        "confidence": round(confidence, 1),
        "ai_score":   round(ai_prob, 1),
        "model":      "trained_classifier",
        "features":   {},
        "error":      None,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", action="store_true", help="Train the classifier")
    args = parser.parse_args()
    if args.train:
        train()
    else:
        print("Usage: python voice_classifier_trainer.py --train")