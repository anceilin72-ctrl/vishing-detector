"""
voice_detector_pretrained.py
-----------------------------
Uses a pretrained deepfake/spoofing detection model from SpeechBrain.
No training data needed — works out of the box.

Install:
    pip install speechbrain torchaudio torch

How it works:
    Uses the AASIST model trained on ASVspoof2019 dataset — the standard
    benchmark for detecting synthetic/AI-generated speech.
"""

import io
import numpy as np

# ── Pretrained model (SpeechBrain AASIST) ────────────────────────────────────
try:
    import torch
    import torchaudio
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    from speechbrain.inference.classifiers import foreign_class
    SPEECHBRAIN_AVAILABLE = True
except ImportError:
    SPEECHBRAIN_AVAILABLE = False


# Lazy-load the model once and reuse
_model = None

def _load_model():
    global _model
    if _model is None:
        print("⏳ Loading pretrained deepfake detection model (first run only)...")
        try:
            _model = foreign_class(
                source="speechbrain/asvspoof-cqtresnet-ecapa",
                pymodule_file="custom_interface.py",
                classname="CustomEncoderWav2VecClassifier",
                savedir="pretrained_models/asvspoof"
            )
            print("✅ Pretrained model loaded.")
        except Exception as e:
            print(f"❌ Could not load pretrained model: {e}")
            _model = None
    return _model


def detect_with_pretrained(audio_bytes: bytes) -> dict:
    """
    Run pretrained ASVspoof model on audio bytes.
    Returns same dict format as voice_detector.py for drop-in compatibility.
    """
    if not TORCH_AVAILABLE:
        return _error("torch not installed. Run: pip install torch torchaudio")
    if not SPEECHBRAIN_AVAILABLE:
        return _error("speechbrain not installed. Run: pip install speechbrain")

    model = _load_model()
    if model is None:
        return _error("Pretrained model failed to load.")

    try:
        # Load audio from bytes
        waveform, sr = torchaudio.load(io.BytesIO(audio_bytes))

        # Resample to 16kHz if needed
        if sr != 16000:
            resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=16000)
            waveform = resampler(waveform)

        # Model expects mono
        if waveform.shape[0] > 1:
            waveform = waveform.mean(dim=0, keepdim=True)

        # Run inference
        out_prob, score, index, label = model.classify_batch(waveform)

        # SpeechBrain ASVspoof: label "bonafide" = human, "spoof" = AI
        is_spoof   = label[0].strip().lower() == "spoof"
        confidence = float(torch.max(out_prob).item()) * 100

        if is_spoof:
            ai_score = confidence
            result_label = "AI Generated"
        else:
            ai_score = 100 - confidence
            result_label = "Human"

        return {
            "label":      result_label,
            "confidence": round(confidence, 1),
            "ai_score":   round(ai_score, 1),
            "model":      "SpeechBrain AASIST (pretrained)",
            "features":   {},
            "error":      None,
        }

    except Exception as e:
        return _error(f"Inference failed: {e}")


def _error(msg: str) -> dict:
    return {
        "label":      "Unknown",
        "confidence": 0.0,
        "ai_score":   0.0,
        "model":      "pretrained",
        "features":   {},
        "error":      msg,
    }