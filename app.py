import streamlit as st
import requests
from database.db import init_db, report_number

# =========================
# Initialize DB
# =========================
init_db()

# =========================
# Page Title
# =========================
st.title("🎤 AI Voice Phishing Detector")

# =========================
# Audio Upload Section using Form
# =========================
with st.form("audio_form", clear_on_submit=True):
    uploaded_audio = st.file_uploader("Upload Audio File", type=["wav", "mp3"])
    analyze_btn = st.form_submit_button("Analyze")

    if analyze_btn and uploaded_audio:
        st.audio(uploaded_audio)

        files = {"file": uploaded_audio.getvalue()}
        try:
            response = requests.post("http://127.0.0.1:8000/analyze", files=files)
            if response.status_code == 200:
                result = response.json()
                risk = result.get("risk_score", 0)
                language = result.get("language", "Unknown")
                keywords = result.get("keywords", [])

                # Display risk level
                if risk > 60:
                    st.error("⚠ High Risk Vishing Call")
                elif risk > 30:
                    st.warning("⚠ Suspicious Call")
                else:
                    st.success("✅ Safe Call")

                # Display metrics
                st.metric("Risk Score", f"{risk:.2f}%")
                st.write("🌍 Language:", language)
                st.write("🔍 Keywords:", ", ".join(keywords))

            else:
                st.error(f"Error analyzing audio: {response.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("⚠ Cannot connect to the analysis server. Make sure FastAPI is running.")

# =========================
# Transcript Section
# =========================
st.markdown("""
<div class="vg-section-label">05 &nbsp; Transcript</div>
""", unsafe_allow_html=True)

# =========================
# Report Spam Number Section
# =========================
st.subheader("📞 Report Spam Number")

# Initialize session_state key safely
if "report_number_input" not in st.session_state:
    st.session_state["report_number_input"] = ""

# Text input for phone number
number = st.text_input("Enter Phone Number", key="report_number_input")

# Callback function for report button
def report_callback():
    if st.session_state["report_number_input"].strip():
        report_number(st.session_state["report_number_input"])
        st.success("Number reported successfully!")
        # Reset input field safely
        st.session_state["report_number_input"] = ""

# Report button
st.button("Report", on_click=report_callback)