import whisper
import numpy as np

model = whisper.load_model("tiny")

WHISPER_LANG_MAP = {
    "ta": "Tamil",
    "hi": "Hindi",
    "en": "English",
    "te": "Tamil",   # Whisper sometimes confuses Tamil/Telugu
    "ml": "Tamil",   # and Malayalam
}

def speech_to_text(file_path: str) -> str:
    try:
        # Step 1: Detect language directly from audio signal
        audio = whisper.load_audio(file_path)
        audio_trimmed = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio_trimmed).to(model.device)
        _, probs = model.detect_language(mel)

        # Pick language with highest probability
        top_lang = max(probs, key=probs.get)
        top_prob = float(probs[top_lang])
        print(f"🌍 Whisper lang: {top_lang} ({top_prob:.0%})")

        # Store for api.py
        speech_to_text.whisper_lang     = top_lang
        speech_to_text.whisper_lang_prob = top_prob

        # Step 2: Transcribe forcing detected language
        result = model.transcribe(
            file_path,
            fp16=False,
            language=top_lang,
        )
        return result["text"].strip()

    except Exception as e:
        print("❌ Whisper Error:", e)
        speech_to_text.whisper_lang      = ""
        speech_to_text.whisper_lang_prob = 0.0
        return ""

speech_to_text.whisper_lang      = ""
speech_to_text.whisper_lang_prob = 0.0