import numpy as np

def detect_voice_authenticity(features):
    """
    Dummy logic (replace with ML later)
    """

    # Example logic based on feature variance
    variance = np.var(features)

    if variance < 0.01:
        return "AI Generated", 85.0
    elif variance < 0.05:
        return "Suspicious", 60.0
    else:
        return "Human", 90.0