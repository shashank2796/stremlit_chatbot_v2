import streamlit as st
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text
from audio_recorder_streamlit import audio_recorder
from streamlit_float import float_init
import os
import time
import tempfile
import streamlit as st
from utils import (
    get_answer,
    text_to_speech,
    autoplay_audio,
    speech_to_text,
)
from audio_recorder_streamlit import audio_recorder
from streamlit_float import float_init
import os

float_init()
st.title("🎙️ KION India Chatbot")
# ---------- SESSION STATE ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

# welcome audio only once
if "welcome_played" not in st.session_state:
    st.session_state.welcome_played = False
    # play_welcome_audio()
if "stage" not in st.session_state:          # 🔑 add this line
    st.session_state.stage = 0         # 1 = Q1, 2 = Q2, 3 = free chat

# ---------- QUESTION BANK ----------
QUESTIONS = {
    1: {
        "text": "How was your flight?",
        "positive": ["yes", "good", "great", "awesome", "fine"],
        "negative": ["no", "not good", "bad", "terrible", "worst"],
        "reply_pos": "That’s wonderful to hear! I hope the rest of your trip is just as smooth.",
        "reply_neg": "Ooh! Sorry to hear that. Let’s make the rest of your time here enjoyable.",
    },
    2: {
        "text": "I hope you’re excited to be in KTCI India!",
        "positive": ["yes", "very excited", "super excited", "can’t wait"],
        "negative": ["no", "not that much", "not really", "kind of"],
        "reply_pos": "Fantastic! We’re thrilled to have you.",
        "reply_neg": "We’ll make you happy with other work, experiments, and the team.",
    },
}

# ---------- UTILITY ----------
def speak(text: str, delay: float):
    """Return path to audio file AND block."""
    tts = gTTS(text=text, lang="en")
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmp.name)
    autoplay_audio(tmp.name)
    time.sleep(delay)
    return tmp.name

# ---------- SEQUENCE ON FIRST LOAD ----------
if st.session_state.stage == 0 and not st.session_state.welcome_played:
    f1 = speak("Hi welcome to India, hope you had a nice flight. Let's speed you up!! Welcome onboard.", 5)
    st.session_state.stage = 1
    time.sleep(0.5)                       # small gap
    f2 = speak(QUESTIONS[1]["text"], 2.5)
    st.session_state.messages.append({"role": "assistant", "content": QUESTIONS[1]["text"]})
    os.remove(f1); os.remove(f2) 

# ---------- FOOTER MIC ----------
footer_container = st.container()
with footer_container:
    audio_bytes = audio_recorder()

# ---------- DISPLAY CHAT ----------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# ---------- VOICE INPUT ----------
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

            # ---------- BRANCHING LOGIC ----------
            stage = st.session_state.stage
            if stage in (1, 2):
                q = QUESTIONS[stage]
                answer = transcript.lower()
                reply = (
                    q["reply_pos"]
                    if any(p in answer for p in q["positive"])
                    else q["reply_neg"]
                )
                speak(reply, 2.5)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.session_state.stage += 1

                # queue next question or switch to open chat
                if st.session_state.stage == 2:
                    time.sleep(0.5)
                    speak(QUESTIONS[2]["text"], 2)
                    st.session_state.messages.append({"role": "assistant", "content": QUESTIONS[2]["text"]})
                elif st.session_state.stage == 3:
                    pass  # free chat starts after next user utterance

            elif stage == 3:  # free chat
                with st.chat_message("assistant"):
                    with st.spinner("Thinking🤔..."):
                        response = get_answer(st.session_state.messages)
                    speak(response, 3)
                    st.write(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

footer_container.float("bottom: 0rem;")






# float_init()

# --- SESSION STATE ---
# if "messages" not in st.session_state:
#     st.session_state.messages = [{"role": "assistant", "content": "Hi! How may I assist you today?"}]

# st.title("🎙️ Audio-to-Audio Chatbot (Gemini)")

# --- SESSION STATE ---
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# st.title("🎙️ KION India Chatbot")

# # --- PLAY WELCOME AUDIO ON FIRST LOAD ---
# if "welcome_played" not in st.session_state:
#     play_welcome_audio()
#     st.session_state.welcome_played = True

# # --- FOOTER MICROPHONE ---
# footer_container = st.container()
# with footer_container:
#     audio_bytes = audio_recorder()

# # --- CHAT DISPLAY ---
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.write(message["content"])

# # --- VOICE INPUT PROCESSING ---
# if audio_bytes:
#     with st.spinner("Transcribing..."):
#         tmp_audio = "temp_audio.mp3"
#         with open(tmp_audio, "wb") as f:
#             f.write(audio_bytes)
#         transcript = speech_to_text(tmp_audio)
#         if transcript:
#             st.session_state.messages.append({"role": "user", "content": transcript})
#             with st.chat_message("user"):
#                 st.write(transcript)
#             os.remove(tmp_audio)

# # --- GENERATE RESPONSE & AUDIO ---
# if st.session_state.messages and st.session_state.messages[-1]["role"] != "assistant":
#     with st.chat_message("assistant"):
#         with st.spinner("Thinking🤔..."):
#             final_response = get_answer(st.session_state.messages)
#         with st.spinner("Generating audio response..."):
#             audio_file = text_to_speech(final_response)
#             autoplay_audio(audio_file)
#         st.write(final_response)
#         st.session_state.messages.append({"role": "assistant", "content": final_response})
#         os.remove(audio_file)

# footer_container.float("bottom: 0rem;")
