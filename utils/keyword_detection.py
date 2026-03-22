"""
keyword_detection.py — Multilingual vishing keyword detector
Supports: English, Tamil (script + Tanglish), Hindi
"""

# =============================================================================
# Tanglish keywords
# =============================================================================
KEYWORDS_TANGLISH = [
    "bank", "hdfc", "sbi", "icici", "axis", "kotak", "canara",
    "bank la erunthu", "bank lerunthu", "bank lirunthu",
    "nanga bank", "bank officer", "bank staff", "bank la pesurom",
    "vanthu pesurom", "bank ku pesurom",
    "vanthutu bank", "vanthutu bank la erunthu",
    # Card related
    "card", "card mela", "card number", "card la",
    "16 numbers", "16 digit", "card details",
    "credit card", "debit card", "atm card",
    "number enter", "number sollu", "number kudu",
    "unga card mela", "card mela oru 16",
    "number enter panitom", "enter panitom",
    # OTP — all variants Whisper might produce
    "otp", "otp varum", "otp sollu", "otp soningana", "otp kudu",
    "otp thirupi", "otp share", "otp solunga", "otp sonninga",
    "antha otp", "otp number", "otp varuma", "otp sollunga",
    "one time password", "otp enter", "otp type",
    "oyp", "antha oyp", "oyp matum", "antha oyp matum",
    "otp matum", "otp matum sollunga", "otp matum soningana",
    "konja soningana", "matum konja soningana",
    "otp matum kudunga", "otp matum thirupi",
    "phone ku otp varum", "phone ku oru otp",
    # Transaction
    "transaction", "transaction proceed", "proceed paniruvom",
    "proceed panlam", "transaction panrom", "payment proceed",
    "transfer", "transfer panrom", "amount transfer",
    "transaction proceed paniruvom", "nanga transaction proceed",
    # Verification
    "verify", "verify pannunga", "verify panna",
    "confirm", "confirm pannunga", "confirm panna",
    "enter pannunga", "enter panitom", "enter panni",
    # Urgency
    "urgent", "urgent ah", "immediate", "ipove",
    "ipo sollu", "ipo kudu", "wait pannathinga",
    "block aagum", "block agum", "block paniduvom",
    "suspend aagum", "close aagum", "cancel aagum",
    # Authority
    "police", "police varum", "case podum", "arrest aaguvinga",
    "court", "court notice", "rbi", "rbi officer",
    "government", "officer", "department", "customer care", "helpline",
    # Social engineering
    "unga account", "unga card", "unga otp",
    "thirupi sollu", "thirupi kudu", "thirupi soningana",
    "number kudunga", "details kudunga", "sollunga",
    # Full phrases from actual audio
    "otp sollunga nanga proceed panrom",
    "card number sollunga", "account block agum",
    "verify panna otp varum", "bank la erunthu pesrom",
    "nanga vanthutu bank la erunthu pesurom",
    "unga phone ku oru otp varum",
    "antha otp matum soningana nanga transaction proceed paniruvom",
    "16 numbers erukum antha number enter panitom",
]

# =============================================================================
# English keywords
# =============================================================================
KEYWORDS_ENGLISH = [
    "account", "blocked", "suspended", "frozen", "deactivated",
    "bank", "credit card", "debit card", "loan", "emi",
    "otp", "one time password", "pin", "password", "verify", "verification",
    "authenticate", "authentication", "cvv", "expiry",
    "urgent", "immediately", "expire", "deadline", "last chance",
    "warning", "alert", "action required", "final notice",
    "aadhaar", "aadhar", "pan card", "kyc", "know your customer",
    "social security", "date of birth", "dob",
    "transfer", "transaction", "payment", "refund", "cashback",
    "reward", "prize", "lottery", "winner", "claim",
    "rbi", "irs", "police", "court", "legal action", "arrest",
    "income tax", "government", "officer",
    "share your otp", "send otp", "click this link",
    "press one", "dial now", "call back immediately",
]

# =============================================================================
# Tamil script keywords — confirmed from actual Whisper transcriptions
# =============================================================================
KEYWORDS_TAMIL = [
    # Account
    "கணக்கு", "முடக்கு", "முடக்குப்", "தடுக்கப்பட்டது",
    "நிறுத்தப்பட்டது", "வங்கி", "வங்கில்", "மங்கில்", "இரணத்து",
    # OTP
    "ஒடி பேசு", "ஒடி", "ஒலுங்கள்", "ஓடிபி", "ஒரு நேய் ஒடி",
    "கடவுச்சொல்", "சரிபார்க்க", "சரிபார்",
    # Urgency
    "அவசரம்", "உடனடியாக", "காலாவதி", "எச்சரிக்கை", "முடக்கப்",
    "அலர்ட்", "கடைசி வாய்ப்பு", "இறுதி அறிவிப்பு",
    # Personal info
    "ஆதார்", "பான் கார்டு", "கேஒய்சி", "பிறந்த தேதி",
    # Money
    "பரிமாற்றம்", "பணம்", "திரும்பப் பெறுதல்", "பரிசு",
    "லாட்டரி", "வெற்றி", "கோர",
    # Authority
    "ஆர்பிஐ", "போலீஸ்", "நீதிமன்றம்", "அரசு", "அதிகாரி",
    "வரி", "சட்ட நடவடிக்கை", "கைது",
    # Actions
    "அனுப்பு", "பகிர்", "கிளிக்", "இணைப்பு",
    # Phrases
    "உங்கள் கணக்கு", "கணக்கு முடக்கு", "வணக்கம் நான்",
]

# =============================================================================
# Hindi keywords
# =============================================================================
KEYWORDS_HINDI = [
    "खाता", "बंद", "निलंबित", "बैंक", "क्रेडिट कार्ड", "डेबिट कार्ड", "लोन",
    "ओटीपी", "पासवर्ड", "सत्यापित", "पिन", "सीवीवी",
    "तुरंत", "अभी", "अंतिम", "चेतावनी", "अलर्ट", "जरूरी",
    "आधार", "पैन कार्ड", "केवाईसी", "जन्म तिथि",
    "ट्रांसफर", "भुगतान", "वापसी", "पुरस्कार", "लॉटरी",
    "आरबीआई", "पुलिस", "अदालत", "सरकार", "अधिकारी", "गिरफ्तार",
    "भेजें", "साझा करें", "क्लिक", "लिंक", "डाउनलोड",
]

# Master list
ALL_KEYWORDS = (
    KEYWORDS_TANGLISH +
    KEYWORDS_ENGLISH +
    KEYWORDS_TAMIL +
    KEYWORDS_HINDI
)

# =============================================================================
# Normalization — display clean English labels in UI
# =============================================================================
NORMALIZE = {
    # Tanglish
    "vanthutu bank": "bank impersonation",
    "vanthutu bank la erunthu": "bank impersonation",
    "unga card mela": "card details",
    "card mela oru 16": "card number",
    "number enter panitom": "card number entered",
    "enter panitom": "details entered",
    "oyp": "otp", "antha oyp": "otp", "oyp matum": "otp",
    "antha oyp matum": "otp", "otp matum": "otp",
    "otp matum sollunga": "otp", "otp matum soningana": "otp",
    "konja soningana": "share details",
    "matum konja soningana": "share details",
    "otp matum kudunga": "otp", "otp matum thirupi": "otp",
    "phone ku otp varum": "otp incoming",
    "phone ku oru otp": "otp incoming",
    "transaction proceed paniruvom": "transaction fraud",
    "nanga transaction proceed": "transaction fraud",
    "nanga vanthutu bank la erunthu pesurom": "bank impersonation",
    "unga phone ku oru otp varum": "otp incoming",
    "antha otp matum soningana nanga transaction proceed paniruvom": "otp fraud",
    "16 numbers erukum antha number enter panitom": "card number",
    "bank lirunthu": "bank impersonation", "nanga bank": "bank impersonation",
    "bank la pesurom": "bank impersonation", "vanthu pesurom": "bank impersonation",
    "card mela": "card details", "16 numbers": "card number",
    "16 digit": "card number", "number enter": "card number",
    "number sollu": "share details", "number kudu": "share details",
    "otp varum": "otp", "otp sollu": "otp", "otp soningana": "otp",
    "otp kudu": "otp", "otp thirupi": "otp", "otp share": "otp",
    "otp solunga": "otp", "otp sonninga": "otp", "antha otp": "otp",
    "otp sollunga": "otp", "otp enter": "otp", "otp type": "otp",
    "transaction proceed": "transaction", "proceed paniruvom": "transaction",
    "proceed panlam": "transaction", "payment proceed": "transaction",
    "transfer panrom": "transfer", "amount transfer": "transfer",
    "verify pannunga": "verify", "verify panna": "verify",
    "confirm pannunga": "confirm", "enter pannunga": "verify",
    "enter panitom": "verify", "block aagum": "account blocked",
    "block agum": "account blocked", "block paniduvom": "account blocked",
    "suspend aagum": "suspended", "close aagum": "account closed",
    "police varum": "police threat", "case podum": "legal threat",
    "arrest aaguvinga": "arrest threat", "court notice": "legal threat",
    "unga account": "account", "unga card": "card details",
    "unga otp": "otp", "thirupi sollu": "share details",
    "thirupi kudu": "share details", "thirupi soningana": "share details",
    "details kudunga": "share details", "sollunga": "share details",
    "otp sollunga nanga proceed panrom": "otp fraud",
    "card number sollunga": "card number",
    "account block agum": "account blocked",
    "verify panna otp varum": "otp verification",
    "bank la erunthu pesrom": "bank impersonation",
    # Tamil script
    "கணக்கு": "account", "முடக்கு": "blocked", "முடக்குப்": "blocked",
    "தடுக்கப்பட்டது": "blocked", "நிறுத்தப்பட்டது": "suspended",
    "வங்கி": "bank", "வங்கில்": "bank", "மங்கில்": "bank",
    "இரணத்து": "from bank",
    "ஒடி பேசு": "otp", "ஒடி": "otp", "ஒலுங்கள்": "share",
    "ஓடிபி": "otp", "ஒரு நேய் ஒடி": "otp",
    "கடவுச்சொல்": "password", "சரிபார்க்க": "verify", "சரிபார்": "verify",
    "அவசரம்": "urgent", "உடனடியாக": "immediately",
    "காலாவதி": "expire", "எச்சரிக்கை": "warning", "முடக்கப்": "blocked",
    "அலர்ட்": "alert", "கடைசி வாய்ப்பு": "last chance",
    "இறுதி அறிவிப்பு": "final notice",
    "ஆதார்": "aadhaar", "பான் கார்டு": "pan card", "கேஒய்சி": "kyc",
    "பிறந்த தேதி": "date of birth", "பரிமாற்றம்": "transfer",
    "பணம்": "payment", "திரும்பப் பெறுதல்": "refund",
    "பரிசு": "prize", "லாட்டரி": "lottery", "வெற்றி": "winner",
    "ஆர்பிஐ": "rbi", "போலீஸ்": "police", "நீதிமன்றம்": "court",
    "அரசு": "government", "அதிகாரி": "officer",
    "வரி": "income tax", "கைது": "arrest",
    "அனுப்பு": "send", "பகிர்": "share", "கிளிக்": "click",
    "இணைப்பு": "link", "உங்கள் கணக்கு": "your account",
    "கணக்கு முடக்கு": "account blocked", "வணக்கம் நான்": "bank greeting",
    # Hindi
    "खाता": "account", "बंद": "blocked", "बैंक": "bank",
    "ओटीपी": "otp", "पासवर्ड": "password", "पिन": "pin",
    "तुरंत": "urgent", "चेतावनी": "warning", "जरूरी": "urgent",
    "आधार": "aadhaar", "पैन कार्ड": "pan card", "केवाईसी": "kyc",
    "ट्रांसफर": "transfer", "भुगतान": "payment", "पुरस्कार": "prize",
    "लॉटरी": "lottery", "आरबीआई": "rbi", "पुलिस": "police",
    "अदालत": "court", "सरकार": "government", "अधिकारी": "officer",
    "गिरफ्तार": "arrest", "भेजें": "send", "लिंक": "link",
}

# =============================================================================
# Detection function
# =============================================================================
def detect_keywords(text: str) -> list:
    if not text or not text.strip():
        return []

    text_lower = text.lower().strip()
    found = []

    for keyword in ALL_KEYWORDS:
        kw = keyword.lower().strip()
        if kw and kw in text_lower:
            label = NORMALIZE.get(keyword, keyword)
            if label not in found:
                found.append(label)

    return found