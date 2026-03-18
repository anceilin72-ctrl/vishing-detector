import whisper

# Load model once (fast after first load)
model = whisper.load_model("base")

def speech_to_text(file_path):
    try:
        result = model.transcribe(file_path)
        text = result["text"].strip()
        return text
    except Exception as e:
        print("❌ Whisper Error:", e)
        return ""