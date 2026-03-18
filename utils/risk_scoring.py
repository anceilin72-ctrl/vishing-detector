def calculate_risk(audio_score, text_score, keyword_score):
    risk = (0.5 * audio_score + 0.3 * text_score + 0.2 * keyword_score) * 100
    return min(risk, 100)