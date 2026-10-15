import streamlit as st
from groq import Groq

st.set_page_config(page_title="Hashir Ali AI", page_icon="👑", layout="centered")

# SIMPLE WHATSAPP THEME - LIGHT, NO HANG
st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
.stApp {background-color: #0b141a;}
.stChatMessage {background-color: #202c33; border-radius: 12px; margin: 5px 0;}
.stChatMessage[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background-color: #005c4b;
}
.stTextInput input {
    background-color: #2a3942 !important;
    border-radius: 25px !important;
    border: none !important;
    color: white !important;
    padding: 12px 18px !important;
}
.stButton button {
    border-radius: 50% !important;
    border: none !important;
    height: 48px;
    width: 48px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h3 style='color:white; text-align:center; margin-bottom:0;'>👑 Hashir Ali AI</h3><p style='color:#8696a0; text-align:center; font-size:13px;'>🟢 Online | WhatsApp Style</p>", unsafe_allow_html=True)

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY in Secrets!")
    st.stop()

SYSTEM_PROMPT = {"role": "system", "content": "You are Hashir Ali AI from Peshawar. Reply in same language user uses. Default English. Short, friendly, WhatsApp style."}

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Salam Hashir! 👑 New light version - No more hang! How can I help?"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---- WHATSAPP BOTTOM BAR - FIXED, NO HANG ----
st.markdown("---")
c1, c2, c3, c4 = st.columns([1, 6, 1, 1])

with c1:
    with st.popover("＋", use_container_width=True):
        st.caption("Attach")
        uploaded = st.file_uploader("📎 File / Photo", type=["png","jpg","jpeg","pdf","txt"], label_visibility="collapsed")
        if uploaded:
            st.success(uploaded.name)

with c2:
    user_text = st.text_input("message", placeholder="Type a message", label_visibility="collapsed", key="user_input")

with c3:
    with st.popover("📷", use_container_width=True):
        st.caption("Camera")
        cam_file = st.camera_input("Take photo", label_visibility="collapsed")
        if cam_file:
            st.image(cam_file)

with c4:
    send_clicked = st.button("➤", key="send", use_container_width=True)

# Voice in sidebar - stable
with st.sidebar:
    st.header("👑 Features")
    voice = st.audio_input("🎤 Voice Message")
    if voice:
        txt = client.audio.transcriptions.create(file=("a.wav", voice.getvalue()), model="whisper-large-v3",
