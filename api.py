from fastapi import FastAPI, UploadFile, File
import shutil
import sys
import os
import time

# Fix module path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Imports
from utils.preprocess import load_audio, normalize_audio
from utils.feature_extraction import extract_features
from utils.speech_to_text import speech_to_text
from utils.language_detect import detect_language
from utils.keyword_detection import detect_keywords
from utils.risk_scoring import calculate_risk
from models.dummy_model import predict_audio, predict_text

# ✅ NEW: Voice authenticity
from models.voice_authenticity import detect_voice_authenticity

app = FastAPI()

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):

    try:
        start_time = time.time()
        print("🚀 Processing started...")

        # -------------------------
        # SAVE FILE
        # -------------------------
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print("✅ File saved")

        # -------------------------
        # AUDIO PROCESSING
        # -------------------------
        y, sr = load_audio(file_path)
        y = normalize_audio(y)
        print("✅ Audio processed")

        # -------------------------
        # FEATURE EXTRACTION
        # -------------------------
        features = extract_features(y, sr)
        print("✅ Features extracted")

        # -------------------------
        # 🎤 VOICE AUTHENTICITY DETECTION
        # -------------------------
        voice_type, confidence = detect_voice_authenticity(features)
        print("🎤 Voice Type:", voice_type)
        print("🔍 Confidence:", confidence)

        # -------------------------
        # AUDIO MODEL
        # -------------------------
        audio_score = predict_audio(features)
        print("🎧 Audio Score:", audio_score)

        # -------------------------
        # SPEECH TO TEXT
        # -------------------------
        try:
            text = speech_to_text(file_path).strip()
        except Exception as e:
            print("❌ Speech Error:", e)
            text = ""

        print("📝 Transcribed Text:", text)

        # -------------------------
        # SAFE FALLBACKS
        # -------------------------
        if text == "":
            text_score = 0
            keywords = []
            language = "Unknown"
        else:
            text_score = predict_text(text)
            keywords = detect_keywords(text)
            language = detect_language(text)

        print("🧠 Text Score:", text_score)
        print("🔍 Keywords:", keywords)
        print("🌍 Language:", language)

        # -------------------------
        # RISK CALCULATION
        # -------------------------
        keyword_score = len(keywords) / 5 if keywords else 0
        risk = calculate_risk(audio_score, text_score, keyword_score)

        print("⚠ Final Risk:", risk)
        print("⏱ Total Time:", time.time() - start_time)

        # -------------------------
        # RESPONSE
        # -------------------------
        return {
            "risk_score": float(risk),
            "language": language,
            "keywords": keywords,
            "text": text,
            "voice_type": voice_type,       # ✅ added
            "confidence": confidence        # ✅ added
        }

    except Exception as e:
        print("❌ ERROR:", e)
        return {"error": str(e)}