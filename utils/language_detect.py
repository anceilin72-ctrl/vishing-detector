"""
language_detect.py — Tamil, Hindi, English only. No langdetect library.
"""

TAMIL_UNICODE_START = 0x0B80
TAMIL_UNICODE_END   = 0x0BFF
HINDI_UNICODE_START = 0x0900
HINDI_UNICODE_END   = 0x097F

TANGLISH_INDICATORS = [
    "unga", "nanga", "sollu", "sollunga", "solunga", "pannunga",
    "panna", "panrom", "paniruvom", "varum", "varuma", "vanthu",
    "erunthu", "lerunthu", "lirunthu", "iruku", "irukku",
    "illai", "ille", "enna", "epdi", "ethuku", "yenna",
    "antha", "inga", "ange", "inge", "apram", "appo",
    "konjam", "romba", "vera", "kooda", "kuda", "mela",
    "la erunthu", "ku pesurom", "pesurom", "pesuvom",
    "thirupi", "thirupu", "kudunga", "kudu",
    "aagum", "agum", "aachu", "aagathu",
    "parunga", "paaru", "pakurom",
    "bank la", "card la", "account la",
    "otp sollu", "otp kudu", "otp varum",
    "anna", "akka", "ayya", "thambi", "thanga",
    "vanakkam", "nandri", "seri", "sari",
    "pongo", "vango", "thenga",
]

def detect_language(text: str) -> str:
    if not text or not text.strip():
        return "Unknown"
    t = text.strip()
    tl = t.lower()

    # Tamil script
    if any(TAMIL_UNICODE_START <= ord(c) <= TAMIL_UNICODE_END for c in t):
        return "Tamil"
    # Hindi script
    if any(HINDI_UNICODE_START <= ord(c) <= HINDI_UNICODE_END for c in t):
        return "Hindi"
    # Tanglish
    if any(word in tl for word in TANGLISH_INDICATORS):
        return "Tamil"
    return "English"