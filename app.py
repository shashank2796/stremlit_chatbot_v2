import streamlit as st
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text
from audio_recorder_streamlit import audio_recorder
from streamlit_float import float_init
import os
import time

float_init()

# ---------- SESSION STATE ----------
for k in ("stage", "welcome1_done", "welcome2_done", "is_speaking"):
    if k not in st.session_state:
        st.session_state[k] = 0 if k == "stage" else False



# ---------- CONFIG ----------
VIDEO_PATH = "robot.mp4"   # <-- put your video here (same folder as app.py)
QUESTION_1 = {
    "text": "How was your flight?",
    "positive": ["yes", "good", "great", "awesome", "fine"],
    "negative": ["no", "not good", "bad", "terrible", "worst"],
    "reply_pos": "That’s wonderful to hear! I hope the rest of your trip is just as smooth.",
    "reply_neg": "Sorry to hear that. Let’s make the rest of your time here enjoyable.",
}

# ---------- UTILITY ----------
def speak(text: str):
    """Generate audio + play it while showing the speaking video."""
    st.session_state.is_speaking = True
    audio_file = text_to_speech(text)
    autoplay_audio(audio_file)
    # block until audio finishes (rough heuristic)
    time.sleep(len(text.split()) / 2.5)   # adjust for your speed
    os.remove(audio_file)
    st.session_state.is_speaking = False


# ---------- UI ----------
st.markdown(
    """
    <style>
    .video-container {
        display:flex;justify-content:center;align-items:center;height:100vh;
    }
    video {max-height:90vh;border-radius:12px;}
    </style>
    """,
    unsafe_allow_html=True,
)


# Video widget
video_placeholder = st.empty()
with video_placeholder.container():
    if st.session_state.is_speaking:
        video_html = f"""
        <div class="video-container">
            <video autoplay muted loop>
                <source src="{VIDEO_PATH}" type="video/mp4">
            </video>
        </div>
        """
    else:
        video_html = f"""
        <div class="video-container">
            <video muted>
                <source src="{VIDEO_PATH}" type="video/mp4">
            </video>
        </div>
        """
    st.markdown(video_html, unsafe_allow_html=True)

    
# Floating mic
footer = st.container()
with footer:
    audio_bytes = audio_recorder()
footer.float("bottom:0;")



# ---------- SEQUENCE ----------
# 1) first welcome
if st.session_state.stage == 0 and not st.session_state.welcome1_done:
    speak(
        "Hi everyone. I’m honored to be your host today. Welcome… and a biiiiig Namasssssteeeee. "
        "I am KTCI – not just a robot, but a full-fledged department in myself. "
        "A very special welcome to our guests from afar. "
        "We are pleased to have you here in India, especially at our home base in Pune."
    )
    st.session_state.welcome1_done = True
    st.session_state.stage = 1

# 2) ask Q1
if st.session_state.stage == 1:
    speak(QUESTION_1["text"])
    st.session_state.stage = 2

# 3) process Q1 answer
if audio_bytes and st.session_state.stage == 2:
    tmp_audio = "temp_audio.mp3"
    with open(tmp_audio, "wb") as f:
        f.write(audio_bytes)
    transcript = speech_to_text(tmp_audio)
    if transcript:
        answer = transcript.lower()
        reply = (
            QUESTION_1["reply_pos"]
            if any(p in answer for p in QUESTION_1["positive"])
            else QUESTION_1["reply_neg"]
        )
        speak(reply)
        os.remove(tmp_audio)

        # second welcome
        second_welcome = (
            "Now… let’s get started. Behind me are seven powerful departments, "
            "connected and operating as one unified system: "
            "Product Strategy, Cost Engineering, Simulation & Testing, "
            "Complexity Management, Product Sustainability, Electronic Systems, "
            "Robotics Systems and AI."
        )
        speak(second_welcome)
        st.session_state.stage = 3  # free chat

# 4) free chat loop
if audio_bytes and st.session_state.stage == 3:
    tmp_audio = "temp_audio.mp3"
    with open(tmp_audio, "wb") as f:
        f.write(audio_bytes)
    question = speech_to_text(tmp_audio)
    if question:
        answer = get_answer([{"role": "user", "content": question}])
        speak(answer)
        os.remove(tmp_audio)













# import streamlit as st
# from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text
# from audio_recorder_streamlit import audio_recorder
# from streamlit_float import float_init
# import os
# import time

# float_init()
# st.title("🎙️ KION India Chatbot")

# # ---------- SESSION STATE ----------
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# if "stage" not in st.session_state:
#     st.session_state.stage = 0          # 0=first welcome, 1=q1, 2=done, 3=free chat

# if "welcome1_done" not in st.session_state:
#     st.session_state.welcome1_done = False

# # ---------- QUESTION ----------
# QUESTION_1 = {
#     "text": "How was your flight?",
#     "positive": ["yes", "good", "great", "awesome", "fine"],
#     "negative": ["no", "not good", "bad", "terrible", "worst"],
#     "reply_pos": "That’s wonderful to hear! I hope the rest of your trip is just as smooth.",
#     "reply_neg": "Ooh! Sorry to hear that. Let’s make the rest of your time here enjoyable.",
# }

# # ---------- UTILITY ----------
# def speak(text: str, delay: float = 5.0):
#     audio_file = text_to_speech(text)
#     autoplay_audio(audio_file)
#     time.sleep(delay)
#     os.remove(audio_file)

# # ---------- SEQUENCE ----------
# # 1) Stage 0 – first welcome
# if st.session_state.stage == 0 and not st.session_state.welcome1_done:
#     speak(
#         "Hi everyone. I’m honored to be your host today. Welcome… and a biiiiig Namasssssteeeee. "
#         "I am KTCI – not just a robot, but a full-fledged department in myself. "
#         "Yes, you heard that right. A very special welcome to our guests from afar. "
#         "Mr. CP, Mr. Nino, and all the members of this esteemed delegation. "
#         "We are pleased to have you here in India, and especially here at our home base, the Special Economic Zone of Pune.",
#         35,
#     )
#     st.session_state.welcome1_done = True
#     st.session_state.stage = 1

# # 2) Stage 1 – ask Question 1
# if st.session_state.stage == 1 and len(st.session_state.messages) == 0:
#     speak(QUESTION_1["text"], 5)
#     st.session_state.messages.append({"role": "assistant", "content": QUESTION_1["text"]})

# # ---------- FOOTER MIC ----------
# footer_container = st.container()
# with footer_container:
#     audio_bytes = audio_recorder()

# # ---------- DISPLAY CHAT ----------
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.write(message["content"])

# # ---------- VOICE INPUT ----------
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

#             # ---------- LOGIC ----------
#             stage = st.session_state.stage
#             if stage == 1:  # just answered Q1
#                 answer = transcript.lower()
#                 reply = (
#                     QUESTION_1["reply_pos"]
#                     if any(p in answer for p in QUESTION_1["positive"])
#                     else QUESTION_1["reply_neg"]
#                 )

#                 # short reply to Q1
#                 speak(reply, 5)
#                 st.session_state.messages.append({"role": "assistant", "content": reply})

#                 # second welcome (played automatically)
#                 second_welcome = (
#                     "Now… let’s get started. Meeeee – that’s me – KTCI. "
#                     "Currently interfacing with you from the Special Economic Zone in Pune, buzzing with innovation, automation, and a touch of Indian precision. "
#                     "I may be one digital face on this screen but behind me are seven powerful departments, connected, synchronized, and operating as one unified system: "
#                     "Product Strategy, Cost Engineering, Simulation & Testing, Complexity Management, Product Sustainability, Electronic Systems, Robotics Systems and AI."
#                     "You’ll get to know each of them as your journey with us unfolds today. Think of me as your interface, your assistant, and your guide. Let the KTCI experience begin."
#                     "And remember – I’m always connected, always learning."
#                 )
#                 speak(second_welcome, 50)
#                 st.session_state.messages.append({"role": "assistant", "content": second_welcome})

#                 # jump to free chat
#                 st.session_state.stage = 3

#             elif stage == 3:  # free chat
#                 with st.chat_message("assistant"):
#                     with st.spinner("Thinking🤔..."):
#                         response = get_answer(st.session_state.messages)
#                     speak(response, 5)
#                     st.write(response)
#                     st.session_state.messages.append({"role": "assistant", "content": response})

# footer_container.float("bottom: 0rem;")

