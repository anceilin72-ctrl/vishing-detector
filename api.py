from fastapi import FastAPI, UploadFile, File
import sys, os, time
import concurrent.futures as cf

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.preprocess import load_audio, normalize_audio
from utils.feature_extraction import extract_features
from utils.speech_to_text import speech_to_text
from utils.language_detect import detect_language
from utils.keyword_detection import detect_keywords
from utils.risk_scoring import calculate_risk
from models.dummy_model import predict_audio, predict_text
from models.voice_authenticity import detect_voice_authenticity
from voice_detector import detect_voice_type

app = FastAPI()

# Whisper language code → display name
WHISPER_LANG_MAP = {
    "ta": "Tamil",
    "hi": "Hindi",
    "en": "English",
    "te": "Tamil",   # Whisper confuses Tamil/Telugu
    "ml": "Tamil",   # and Malayalam
}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    file_path = None
    try:
        start_time = time.time()

        # ── 1. Save file ──────────────────────────────────────────────────────
        audio_bytes = await file.read()
        file_path   = f"temp_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(audio_bytes)

        # ── 2. Load audio once ────────────────────────────────────────────────
        y, sr = load_audio(file_path)
        y     = normalize_audio(y)

        # ── 3. Run all heavy tasks in parallel ────────────────────────────────
        def run_features():
            feats       = extract_features(y, sr)
            vtype, conf = detect_voice_authenticity(feats)
            ascore      = predict_audio(feats)
            return feats, vtype, conf, ascore

        def run_stt():
            try:
                return speech_to_text(file_path).strip()
            except Exception as e:
                print("❌ STT:", e)
                return ""

        def run_voice_det():
            return detect_voice_type(audio_bytes)

        with cf.ThreadPoolExecutor(max_workers=3) as ex:
            f_feats   = ex.submit(run_features)
            f_stt     = ex.submit(run_stt)
            f_voicdet = ex.submit(run_voice_det)

            features, voice_type, confidence, audio_score = f_feats.result()
            text      = f_stt.result()
            voice_det = f_voicdet.result()

        print(f"✅ Done ({round(time.time()-start_time,1)}s)")

        # ── 4. Language detection ─────────────────────────────────────────────
        # Use Whisper's audio-based language detection (most reliable)
        # Falls back to text-based only if Whisper has low confidence
        whisper_lang = getattr(speech_to_text, "whisper_lang", "")
        whisper_prob = getattr(speech_to_text, "whisper_lang_prob", 0.0)

        if whisper_lang and whisper_prob >= 0.20:
            # Trust Whisper language detection from audio signal
            language = WHISPER_LANG_MAP.get(whisper_lang, "English")
            print(f"🌍 Language: {language} via Whisper ({whisper_prob:.0%})")
        elif text:
            # Fallback: detect from transcribed text
            language = detect_language(text)
            print(f"🌍 Language: {language} via text fallback")
        else:
            language = "Unknown"

        # ── 5. Keywords & risk ────────────────────────────────────────────────
        if text:
            text_score    = predict_text(text)
            keywords      = detect_keywords(text)
        else:
            text_score, keywords = 0, []

        keyword_score = len(keywords) / 5 if keywords else 0
        risk          = calculate_risk(audio_score, text_score, keyword_score)

        print(f"⚠ Risk: {risk:.1f}% | Keywords: {keywords}")

        # ── 6. Cleanup ────────────────────────────────────────────────────────
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

        return {
            "risk_score":    float(risk),
            "language":      language,
            "keywords":      keywords,
            "voice_type":    voice_type,
            "confidence":    confidence,
            "ai_label":      voice_det.get("label", "Unknown"),
            "ai_confidence": voice_det.get("confidence", 0),
            "ai_score":      voice_det.get("ai_score", 0),
        }

    except Exception as e:
        print("❌ ERROR:", e)
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        return {"error": str(e)}


@app.post("/detect-voice-type")
async def detect_voice_type_endpoint(file: UploadFile = File(...)):
    try:
        return detect_voice_type(await file.read())
    except Exception as e:
        return {"label": "Unknown", "confidence": 0.0, "ai_score": 0.0, "features": {}, "error": str(e)}