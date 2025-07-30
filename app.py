import streamlit as st
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text
from audio_recorder_streamlit import audio_recorder
from streamlit_float import float_init
import os

float_init()

# --- SESSION STATE ---
# if "messages" not in st.session_state:
#     st.session_state.messages = [{"role": "assistant", "content": "Hi! How may I assist you today?"}]

# st.title("🎙️ Audio-to-Audio Chatbot (Gemini)")

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- PLAY WELCOME AUDIO ON FIRST LOAD ---
if "welcome_played" not in st.session_state:
    play_welcome_audio()
    st.session_state.welcome_played = True

# --- FOOTER MICROPHONE ---
footer_container = st.container()
with footer_container:
    audio_bytes = audio_recorder()

# --- CHAT DISPLAY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# --- VOICE INPUT PROCESSING ---
if audio_bytes:
    with st.spinner("Transcribing..."):
        tmp_audio = "temp_audio.mp3"
        with open(tmp_audio, "wb") as f:
            f.write(audio_bytes)
        transcript = speech_to_text(tmp_audio)
        if transcript:
            st.session_state.messages.append({"role": "user", "content": transcript})
            with st.chat_message("user"):
                st.write(transcript)
            os.remove(tmp_audio)

# --- GENERATE RESPONSE & AUDIO ---
if st.session_state.messages and st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking🤔..."):
            final_response = get_answer(st.session_state.messages)
        with st.spinner("Generating audio response..."):
            audio_file = text_to_speech(final_response)
            autoplay_audio(audio_file)
        st.write(final_response)
        st.session_state.messages.append({"role": "assistant", "content": final_response})
        os.remove(audio_file)

footer_container.float("bottom: 0rem;")
