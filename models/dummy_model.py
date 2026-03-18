import numpy as np

def predict_audio(features):
    # Dummy AI prediction (replace with trained model later)
    return np.random.uniform(0.4, 0.9)

def predict_text(text):
    if "otp" in text or "bank" in text:
        return 0.9
    return 0.3