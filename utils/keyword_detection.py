def detect_keywords(text):
    keywords = ["otp", "bank", "urgent", "account", "password"]
    found = [word for word in keywords if word in text.lower()]
    return found