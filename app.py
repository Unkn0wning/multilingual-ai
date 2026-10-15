import streamlit as st
from groq import Groq

st.set_page_config(page_title="Hashir Ali AI", page_icon="👑", layout="centered")

# WHATSAPP CSS - Makes it look EXACT like your photo
st.markdown("""
<style>
/* Hide default */
#MainMenu, footer, header {visibility: hidden;}

/* WhatsApp background */
.stApp {background-color: #111b21;}

/* Chat messages */
.stChatMessage {background: transparent; border: none;}
[data-testid="stChatMessageContent"] {border-radius: 8px;}

/* Bottom bar - WhatsApp style */
.bottom-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #202c33;
    padding: 10px 15px;
    display: flex;
    align-items: center;
    gap: 12px;
    z-index: 999;
}

/* Plus icon */
.plus-btn {color: white; font-size: 28px; cursor: pointer;}

/* Text input - rounded grey like WhatsApp */
.wa-input {
    flex: 1;
    background: #2a3942;
    border-radius: 25px;
    border: none;
    padding: 12px 18px;
    color: white;
    outline: none;
}

/* Camera icon */
.camera-btn {color: white; font-size: 24px; cursor: pointer;}

/* Green Mic button */
.mic-btn {
    background: #00a884;
    width: 48px;
    height: 48px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 22px;
    cursor: pointer;
}

.stButton > button {
    background: transparent;
    border: none;
    color: white;
    font-size: 28px;
}

.stTextInput > div > div > input {
    background: #2a3942;
    border-radius: 25px;
    border: none;
    color: white;
    padding: 14px 18px;
}

div[data-testid="column"] {display: flex; align-items: center; justify-content: center;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='color:white; text-align:center;'>👑 Hashir Ali AI</h2><p style='color:#8696a0; text-align:center; margin-top:-15px;'>🟢 Online | WhatsApp Style</p>", unsafe_allow_html=True)

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY in Secrets!")
    st.stop()

SYSTEM_PROMPT = {"role": "system", "content": "You are Hashir Ali AI from Peshawar. Reply in SAME language as user. Default English. Be friendly, short, like WhatsApp friend."}

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Salam Hashir! 👑 WhatsApp layout ready! Type below 👇"}]

# Show messages with space for bottom bar
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(f"<span style='color:white;'>{msg['content']}</span>", unsafe_allow_html=True)

st.markdown("<br><br><br><br>", unsafe_allow_html=True)

# WHATSAPP BOTTOM BAR - EXACT LIKE YOUR PHOTO
col1, col2, col3, col4 = st.columns([0.8, 6, 0.8, 0.9])

with col1:
    plus = st.button("＋", key="plus")
    if plus:
        st.toast("📎 Upload file - Coming!")

with col2:
    prompt = st.chat_input("Type a message...", key="wa_input")

with col3:
    cam = st.button("📷", key="cam")
    if cam:
        st.toast("📸 Camera clicked!")

with col4:
    mic = st.button("🎤", key="mic")
    if mic:
        st.toast("🎙️ Voice - Hold to record!")

# Voice and Camera features in sidebar as backup
with st.sidebar:
    st.markdown("### 👑 Extra")
