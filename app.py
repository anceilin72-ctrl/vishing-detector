import streamlit as st
import requests
from database.db import init_db, report_number

init_db()

st.set_page_config(
    page_title="VishGuard — AI Voice Phishing Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Syne:wght@400;700;800&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: #080c10;
    color: #c8d8e8;
}

.stApp {
    background: #080c10;
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -20%, rgba(0,200,150,0.07) 0%, transparent 70%),
        repeating-linear-gradient(0deg, transparent, transparent 40px, rgba(0,200,150,0.02) 40px, rgba(0,200,150,0.02) 41px),
        repeating-linear-gradient(90deg, transparent, transparent 40px, rgba(0,200,150,0.02) 40px, rgba(0,200,150,0.02) 41px);
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1200px; }

/* ── Hero header ── */
.vg-hero {
    text-align: center;
    padding: 3rem 0 2rem;
    position: relative;
}
.vg-hero-tag {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.3em;
    color: #00c896;
    text-transform: uppercase;
    margin-bottom: 1rem;
    opacity: 0.8;
}
.vg-hero h1 {
    font-size: 3.2rem;
    font-weight: 800;
    line-height: 1.1;
    margin: 0;
    background: linear-gradient(135deg, #ffffff 0%, #00c896 60%, #00a8ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.vg-hero-sub {
    font-size: 1rem;
    color: #6a8a9a;
    margin-top: 0.75rem;
    font-weight: 400;
}
.vg-accent-line {
    width: 60px;
    height: 2px;
    background: linear-gradient(90deg, #00c896, #00a8ff);
    margin: 1.5rem auto 0;
    border-radius: 2px;
}

/* ── Upload zone ── */
.vg-upload-wrapper {
    background: rgba(0,200,150,0.03);
    border: 1px solid rgba(0,200,150,0.15);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin: 2rem 0;
    position: relative;
    overflow: hidden;
}
.vg-upload-wrapper::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, #00c896, transparent);
}
.vg-upload-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.25em;
    color: #00c896;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
}

/* ── Streamlit file uploader restyle ── */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px dashed rgba(0,200,150,0.3) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(0,200,150,0.6) !important;
    background: rgba(0,200,150,0.04) !important;
}
[data-testid="stFileUploadDropzone"] p {
    color: #6a8a9a !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.85rem !important;
}

/* ── Analyze button ── */
[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #00c896 0%, #00a8ff 100%) !important;
    color: #080c10 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 2.5rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 0 20px rgba(0,200,150,0.3) !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
    box-shadow: 0 0 35px rgba(0,200,150,0.5) !important;
    transform: translateY(-1px) !important;
}
[data-testid="stButton"] > button[kind="primary"]:disabled {
    background: rgba(255,255,255,0.05) !important;
    color: #3a5060 !important;
    box-shadow: none !important;
    transform: none !important;
}

/* ── Audio player ── */
audio {
    width: 100%;
    filter: invert(1) hue-rotate(150deg) brightness(0.8);
    border-radius: 8px;
    margin: 1rem 0;
}

/* ── Result cards ── */
.vg-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 1.75rem;
    height: 100%;
    position: relative;
    overflow: hidden;
}
.vg-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,200,150,0.4), transparent);
}
.vg-card-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: #00c896;
    margin-bottom: 1.25rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.vg-card-title::before {
    content: '▸';
    opacity: 0.6;
}

/* ── Risk banner ── */
.vg-banner {
    border-radius: 10px;
    padding: 0.85rem 1.25rem;
    margin-bottom: 1.25rem;
    font-weight: 700;
    font-size: 0.95rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.vg-banner-danger {
    background: rgba(255,60,80,0.1);
    border: 1px solid rgba(255,60,80,0.3);
    color: #ff6070;
}
.vg-banner-warning {
    background: rgba(255,180,0,0.08);
    border: 1px solid rgba(255,180,0,0.25);
    color: #ffb800;
}
.vg-banner-safe {
    background: rgba(0,200,150,0.08);
    border: 1px solid rgba(0,200,150,0.25);
    color: #00c896;
}

/* ── Score display ── */
.vg-score-row {
    display: flex;
    align-items: baseline;
    gap: 0.4rem;
    margin: 0.5rem 0 1rem;
}
.vg-score-num {
    font-family: 'Share Tech Mono', monospace;
    font-size: 2.8rem;
    font-weight: 400;
    line-height: 1;
    color: #ffffff;
}
.vg-score-unit {
    font-family: 'Share Tech Mono', monospace;
    font-size: 1rem;
    color: #6a8a9a;
}
.vg-score-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    color: #6a8a9a;
    text-transform: uppercase;
    margin-bottom: 0.25rem;
}

/* ── Progress bar ── */
.vg-bar-wrap {
    background: rgba(255,255,255,0.05);
    border-radius: 4px;
    height: 6px;
    margin: 0.5rem 0 0.25rem;
    overflow: hidden;
}
.vg-bar-fill-safe   { height: 100%; border-radius: 4px; background: linear-gradient(90deg, #00c896, #00a8ff); }
.vg-bar-fill-warn   { height: 100%; border-radius: 4px; background: linear-gradient(90deg, #ffb800, #ff8c00); }
.vg-bar-fill-danger { height: 100%; border-radius: 4px; background: linear-gradient(90deg, #ff4040, #ff6070); }
.vg-bar-caption {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.58rem;
    color: #3a5060;
    letter-spacing: 0.1em;
    display: flex;
    justify-content: space-between;
}

/* ── Tags ── */
.vg-tag-row { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.5rem; }
.vg-tag {
    background: rgba(255,60,80,0.1);
    border: 1px solid rgba(255,60,80,0.2);
    color: #ff8090;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
}

/* ── Info row ── */
.vg-info-row {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    margin: 0.6rem 0;
    font-size: 0.85rem;
}
.vg-info-key {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    color: #3a5060;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    min-width: 80px;
}
.vg-info-val { color: #c8d8e8; }

/* ── Divider ── */
.vg-divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.05);
    margin: 2.5rem 0;
}

/* ── Report section ── */
.vg-report-section {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 1.75rem 2rem;
    position: relative;
    overflow: hidden;
}
.vg-report-section::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,60,80,0.4), transparent);
}
.vg-section-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: #ff6070;
    margin-bottom: 1.25rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.vg-section-title::before { content: '▸'; opacity: 0.6; }

/* ── Text input restyle ── */
[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 8px !important;
    color: #c8d8e8 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.9rem !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: rgba(255,60,80,0.4) !important;
    box-shadow: 0 0 0 2px rgba(255,60,80,0.1) !important;
}

/* ── Report button ── */
[data-testid="stButton"] > button:not([kind="primary"]) {
    background: rgba(255,60,80,0.08) !important;
    color: #ff6070 !important;
    border: 1px solid rgba(255,60,80,0.25) !important;
    border-radius: 8px !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    transition: all 0.2s ease !important;
}
[data-testid="stButton"] > button:not([kind="primary"]):hover {
    background: rgba(255,60,80,0.15) !important;
    border-color: rgba(255,60,80,0.5) !important;
    box-shadow: 0 0 15px rgba(255,60,80,0.2) !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] { color: #00c896 !important; }

/* ── Expander ── */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] summary {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.1em !important;
    color: #6a8a9a !important;
}

/* ── Alerts restyle ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
}

/* ── Metric restyle ── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.02);
    border-radius: 10px;
    padding: 0.75rem 1rem;
}
[data-testid="stMetricLabel"] {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.6rem !important;
    letter-spacing: 0.2em !important;
    color: #3a5060 !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Share Tech Mono', monospace !important;
    color: #ffffff !important;
}

/* ── Footer ── */
.vg-footer {
    text-align: center;
    padding: 2rem 0 1rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    color: #1e3040;
    text-transform: uppercase;
}
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="vg-hero">
    <div class="vg-hero-tag">// threat detection system v2.0</div>
    <h1>VishGuard</h1>
    <div class="vg-hero-sub">AI-powered voice phishing & deepfake audio detection</div>
    <div class="vg-accent-line"></div>
</div>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for key, default in [
    ("audio_bytes", None),
    ("audio_name",  None),
    ("audio_type",  None),
    ("do_analyze",  False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Upload zone ───────────────────────────────────────────────────────────────
st.markdown('<div class="vg-upload-wrapper"><div class="vg-upload-label">// audio input</div>', unsafe_allow_html=True)
uploaded_audio = st.file_uploader(
    "Drop audio file here",
    type=["wav", "mp3", "ogg", "flac"],
    label_visibility="collapsed",
)
st.markdown('</div>', unsafe_allow_html=True)

analyze_btn = st.button("⬡  Run Analysis", type="primary", disabled=uploaded_audio is None)

if analyze_btn and uploaded_audio:
    st.session_state.audio_bytes = uploaded_audio.getvalue()
    st.session_state.audio_name  = uploaded_audio.name
    st.session_state.audio_type  = uploaded_audio.type
    st.session_state.do_analyze  = True

if uploaded_audio is None:
    st.session_state.do_analyze = False

# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.do_analyze and st.session_state.audio_bytes:
    audio_bytes = st.session_state.audio_bytes
    audio_name  = st.session_state.audio_name
    audio_type  = st.session_state.audio_type

    st.audio(audio_bytes)

    with st.spinner("scanning audio signature..."):
        try:
            response = requests.post(
                "http://127.0.0.1:8000/analyze",
                files={"file": (audio_name, audio_bytes, audio_type)},
                timeout=300,
            )

            if response.status_code == 200:
                result = response.json()

                if "error" in result:
                    st.error(f"Analysis error: {result['error']}")
                else:
                    risk          = result.get("risk_score", 0)
                    language      = result.get("language", "Unknown")
                    keywords      = result.get("keywords", [])
                    ai_label      = result.get("ai_label", "Unknown")
                    ai_confidence = result.get("ai_confidence", 0)
                    ai_score      = result.get("ai_score", 0)

                    # ── Risk banner ───────────────────────────────────────────
                    if risk > 60:
                        risk_class = "vg-banner-danger"
                        risk_icon  = "⚠"
                        risk_text  = "HIGH RISK — Vishing Detected"
                    elif risk > 30:
                        risk_class = "vg-banner-warning"
                        risk_icon  = "◈"
                        risk_text  = "SUSPICIOUS — Manual Review Advised"
                    else:
                        risk_class = "vg-banner-safe"
                        risk_icon  = "✓"
                        risk_text  = "SAFE — No Threat Detected"

                    st.markdown(f"""
                    <div class="vg-banner {risk_class}">
                        <span>{risk_icon}</span> {risk_text}
                    </div>
                    """, unsafe_allow_html=True)

                    # ── Two result cards ──────────────────────────────────────
                    col_left, col_right = st.columns(2, gap="medium")

                    # LEFT — Vishing Risk
                    with col_left:
                        # bar color
                        if risk > 60:
                            bar_class = "vg-bar-fill-danger"
                        elif risk > 30:
                            bar_class = "vg-bar-fill-warn"
                        else:
                            bar_class = "vg-bar-fill-safe"

                        kw_tags = "".join([f'<span class="vg-tag">{k}</span>' for k in keywords]) if keywords else '<span style="color:#3a5060;font-family:Share Tech Mono,monospace;font-size:0.75rem">none detected</span>'

                        st.markdown(f"""
                        <div class="vg-card">
                            <div class="vg-card-title">Vishing Risk Analysis</div>
                            <div class="vg-score-label">Risk Score</div>
                            <div class="vg-score-row">
                                <span class="vg-score-num">{risk:.0f}</span>
                                <span class="vg-score-unit">%</span>
                            </div>
                            <div class="vg-bar-wrap">
                                <div class="{bar_class}" style="width:{min(risk,100):.0f}%"></div>
                            </div>
                            <div class="vg-bar-caption"><span>0 — safe</span><span>100 — critical</span></div>
                            <br>
                            <div class="vg-info-row">
                                <span class="vg-info-key">Language</span>
                                <span class="vg-info-val">{language}</span>
                            </div>
                            <div class="vg-info-row" style="align-items:flex-start">
                                <span class="vg-info-key">Keywords</span>
                                <div class="vg-tag-row">{kw_tags}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    # RIGHT — AI vs Human
                    with col_right:
                        if ai_label == "AI Generated":
                            ai_banner_class = "vg-banner-danger"
                            ai_icon = "◉"
                            ai_text = "AI GENERATED VOICE"
                            ai_bar  = "vg-bar-fill-danger"
                        elif ai_label == "Human":
                            ai_banner_class = "vg-banner-safe"
                            ai_icon = "◎"
                            ai_text = "HUMAN VOICE"
                            ai_bar  = "vg-bar-fill-safe"
                        else:
                            ai_banner_class = "vg-banner-warning"
                            ai_icon = "◈"
                            ai_text = "UNCERTAIN"
                            ai_bar  = "vg-bar-fill-warn"

                        st.markdown(f"""
                        <div class="vg-card">
                            <div class="vg-card-title">Voice Authenticity</div>
                            <div class="vg-banner {ai_banner_class}" style="margin-bottom:1rem">
                                {ai_icon} &nbsp; {ai_text}
                            </div>
                            <div class="vg-score-label">AI Probability</div>
                            <div class="vg-score-row">
                                <span class="vg-score-num">{ai_score:.0f}</span>
                                <span class="vg-score-unit">%</span>
                            </div>
                            <div class="vg-bar-wrap">
                                <div class="{ai_bar}" style="width:{min(ai_score,100):.0f}%"></div>
                            </div>
                            <div class="vg-bar-caption"><span>0 — human</span><span>100 — synthetic</span></div>
                            <br>
                            <div class="vg-info-row">
                                <span class="vg-info-key">Confidence</span>
                                <span class="vg-info-val">{ai_confidence:.1f}%</span>
                            </div>
                            <div class="vg-info-row">
                                <span class="vg-info-key">Detection</span>
                                <span class="vg-info-val">Trained Classifier</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)



            else:
                st.error(f"Server error: {response.status_code}")

        except requests.exceptions.ConnectionError:
            st.error("⚠ Cannot connect to FastAPI server. Run: python -m uvicorn api:app --reload")
        except requests.exceptions.Timeout:
            st.error("⚠ Request timed out. Try a shorter audio clip.")

# ── Divider ───────────────────────────────────────────────────────────────────
st.markdown('<hr class="vg-divider">', unsafe_allow_html=True)

# ── Report section ────────────────────────────────────────────────────────────
st.markdown('<div class="vg-report-section"><div class="vg-section-title">Report Spam Number</div>', unsafe_allow_html=True)

if "phone_input" not in st.session_state:
    st.session_state["phone_input"] = ""

st.text_input("Phone number to report", key="phone_input", placeholder="+1 (555) 000-0000", label_visibility="collapsed")

def report_callback():
    if st.session_state["phone_input"].strip():
        report_number(st.session_state["phone_input"])
        st.success(f"✓ {st.session_state['phone_input']} has been reported.")
        st.session_state["phone_input"] = ""

st.button("⚑  Flag Number", on_click=report_callback)
st.markdown('</div>', unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="vg-footer">
    VishGuard &nbsp;·&nbsp; AI Voice Threat Detection &nbsp;·&nbsp; v2.0
</div>
""", unsafe_allow_html=True)