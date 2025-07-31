import os
import google.generativeai as genai
from gtts import gTTS
import streamlit as st
import base64
import tempfile

# 1. Configure Gemini
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash-exp")

SYSTEM = "You are a helpful AI chatbot that answers questions asked by the User."


# ---------------- CHAT ----------------
def get_answer(messages):
    prompt = SYSTEM + "\n" + "\n".join([f"{m['role']}: {m['content']}" for m in messages])
    response = model.generate_content(prompt)
    return response.text

# ---------------- STT ----------------
def speech_to_text(audio_path):
    audio_file = genai.upload_file(audio_path)
    response = model.generate_content(["Please transcribe this audio accurately.", audio_file])
    return response.text.strip()

# ---------------- TTS ----------------
def text_to_speech(text: str) -> str:
    """Return path to an MP3 file with spoken text."""
    tts = gTTS(text=text, lang="en")
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmp.name)
    return tmp.name

# ---------------- AUDIO AUTOPLAY ----------------
def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    html = f"""
    <audio autoplay>
      <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(html, unsafe_allow_html=True)
