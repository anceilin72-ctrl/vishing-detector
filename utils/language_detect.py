from langdetect import detect

def detect_language(text):
    try:
        lang = detect(text)
        mapping = {
            "en": "English",
            "ta": "Tamil",
            "hi": "Hindi"
        }
        return mapping.get(lang, "Unknown")
    except:
        return "Unknown"