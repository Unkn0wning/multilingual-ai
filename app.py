import streamlit as st
from groq import Groq

st.set_page_config(page_title="Hashir Ali AI", page_icon="👑")
st.markdown("<style>#MainMenu,footer,header{visibility:hidden;}.stApp{background:#0b141a;}</style>", unsafe_allow_html=True)

st.title("👑 Hashir Ali AI")
st.caption("🟢 Online | WhatsApp Style | No Error Version")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY in Secrets!")
    st.stop()

SYSTEM = {"role": "system", "content": "You are Hashir Ali AI from Peshawar. Reply in same language as user. Default English. Friendly WhatsApp style."}

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Salam Hashir! 👑 Final fixed version - Ready!"}]

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# WhatsApp style bottom - SIMPLE, NO HANG
prompt = st.chat_input("Type a message... + for file, mic for voice")

# Sidebar for + and Camera and Mic - Stable place
with st.sidebar:
    st.header("👑 WhatsApp Menu")
    st.write("📎 Upload")
    up = st.file_uploader("Photo / File", type=["png","jpg","pdf","txt"])
    if up:
        st.success(up.name)
    st.write("🎤 Voice")
    aud = st.audio_input("Voice")
    if aud:
        st.info("Voice uploaded - Type 'transcribe my voice' to use
