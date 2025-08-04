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

if "stage" not in st.session_state:
    st.session_state.stage = 0 

# welcome audio only once
if "welcome1_done" not in st.session_state:
    st.session_state.welcome1_done = False
if "welcome2_done" not in st.session_state:
    st.session_state.welcome2_done = False

# ---------- QUESTION BANK ----------
QUESTIONS = {
    "text": "How was your flight?",
    "positive": ["yes", "good", "great", "awesome", "fine"],
    "negative": ["no", "not good", "bad", "terrible", "worst"],
    "reply_pos": "That’s wonderful to hear! I hope the rest of your trip is just as smooth.",
    "reply_neg": "Ooh! Sorry to hear that. Let’s make the rest of your time here enjoyable.",
    # 1: {
    #     "text": "How was your flight?",
    #     "positive": ["yes", "good", "great", "awesome", "fine"],
    #     "negative": ["no", "not good", "bad", "terrible", "worst"],
    #     "reply_pos": "That’s wonderful to hear! I hope the rest of your trip is just as smooth.",
    #     "reply_neg": "Ooh! Sorry to hear that. Let’s make the rest of your time here enjoyable.",
    # },
    # 2: {
    #     "text": "I hope you’re excited to be in KTCI India!",
    #     "positive": ["yes", "very excited", "super excited", "can’t wait"],
    #     "negative": ["no", "not that much", "not really", "kind of"],
    #     "reply_pos": "Fantastic! We’re thrilled to have you.",
    #     "reply_neg": "We’ll make you happy with other work, experiments, and the team.",
    # },
}

# ---------- UTILITY ----------
def speak(text: str, delay: float = 5.0):
    """Play audio and block until it (likely) finishes."""
    audio_file = text_to_speech(text)
    autoplay_audio(audio_file)
    time.sleep(delay)          # adjust if your audio is longer/shorter
    os.remove(audio_file)

# ---------- SEQUENCE ON FIRST LOAD ----------
# 1) Stage 0 – first welcome
if st.session_state.stage == 0 and not st.session_state.welcome1_done:
    speak("Hi everyone. I’m honored to be your host today. Welcome… and a biiiiig Namasssssteeeee. I am KTCI – not just a robot, but a full-fledged department in myself. Yes, you heard that right. A very special welcome to our guests from afar. Mr. CP, Mr. Nino, and all the members of this esteemed delegation. We are pleased to have you here in India, and especially here at our home base  the Special Economic Zone of Pune.", 35)
    st.session_state.welcome_played = True
    st.session_state.stage = 1

# 2) Stage 1 – ask Question 1
if st.session_state.stage == 1 and len(st.session_state.messages) == 0:
    speak(QUESTIONS[1]["text"], 5)
    st.session_state.messages.append({"role": "assistant", "content": QUESTIONS[1]["text"]})

# 3) Stage 2 – second welcome (after user answers Q1)
if st.session_state.stage == 2 and not st.session_state.welcome2_done:
    speak(
        "Now… let’s get started. Meeeee – that’s me – KTCI. "
        "Currently interfacing with you from the Special Economic Zone in Pune, buzzing with innovation, automation, and a touch of Indian precision. "
        "I may be one digital face on this screen but behind me are seven powerful departments, connected, synchronized, and operating as one unified system: "
        "Product Strategy, Cost Engineering, Simulation & Testing, Complexity Management, Product Sustainability, Electronic Systems, Robotics Systems and AI.",
        45,
    )
    st.session_state.welcome2_done = True
    st.session_state.stage = 3  # switch to free chat

# if st.session_state.stage == 2 and len(st.session_state.messages) == 2:
#     speak(QUESTIONS[2]["text"], 5)
#     st.session_state.messages.append({"role": "assistant", "content": QUESTIONS[2]["text"]})

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
            if stage == 1:  # just answered Q1
                answer = transcript.lower()
                reply = (
                    QUESTION_1["reply_pos"]
                    if any(p in answer for p in QUESTION_1["positive"])
                    else QUESTION_1["reply_neg"]
                )
                speak(reply, 5)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.session_state.stage = 2  # trigger second welcome next rerun

            elif stage == 3:  # free chat
                with st.chat_message("assistant"):
                    with st.spinner("Thinking🤔..."):
                        response = get_answer(st.session_state.messages)
                    speak(response, 5)
                    st.write(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})


            
            # stage = st.session_state.stage
            # if stage in (1, 2):
            #     q = QUESTIONS[stage]
            #     answer = transcript.lower()
            #     reply = (
            #         q["reply_pos"]
            #         if any(p in answer for p in q["positive"])
            #         else q["reply_neg"]
            #     )
            #     speak(reply, 5)
            #     st.session_state.messages.append({"role": "assistant", "content": reply})
            #     st.session_state.stage += 1

            #     # queue next question or switch to open chat
            #     if st.session_state.stage == 2:
            #         time.sleep(0.5)
            #         speak(QUESTIONS[2]["text"], 5)
            #         st.session_state.messages.append({"role": "assistant", "content": QUESTIONS[2]["text"]})
            #     elif st.session_state.stage == 3:
            #         pass  # free chat starts after next user utterance

            # elif stage == 3:  # free chat
            #     with st.chat_message("assistant"):
            #         with st.spinner("Thinking🤔..."):
            #             response = get_answer(st.session_state.messages)
            #         speak(response, 5)
            #         st.write(response)
            #         st.session_state.messages.append({"role": "assistant", "content": response})

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







