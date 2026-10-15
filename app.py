import streamlit as st
from groq import Groq

st.set_page_config(page_title="Hashir AI", page_icon="👑", layout="centered")

# WHATSAPP DARK THEME - SAFE CSS
st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
.stApp {background-color: #111b21;}
h1, h2, h3, p {color: white!important;}
[data-testid="stChatMessage"] {border-radius: 12px; padding: 10px;}
[data-testid="stChatMessageContent"] {color: white;}
.stChatInput {background-color: #202c33!important;}
.stChatInput input {background-color: #2a3942!important; color: white!important; border-radius: 25px!important;}
</style>
""", unsafe_allow_html=True)

st.title("👑 Hashir Ali AI")
st.caption("🟢 Online | WhatsApp Style")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Salam Hashir! 👑 WhatsApp Dark Ready! Full Pro - Chat Voice Picture File!"}]

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

prompt = st.chat_input("Type a message... + 📷 🎤 in sidebar")

with st.sidebar:
    st.header("WhatsApp Menu")
    st.write("Click arrow to open")
    f = st.file_uploader("Upload Photo File", type=["png","jpg","pdf","txt"])
    if f:
        st.success(f.name)
    v = st.audio_input("Voice Message")
    if v:
        st.success("Voice saved")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        full = ""
        box = st.empty()
        stream = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=st.session_state.messages,
            stream=True
        )
        for c in stream:
            if c.choices[0].delta.content:
                full += c.choices[0].delta.content
                box.markdown(full + "▌")
        box.markdown(full)
        st.session_state.messages.append({"role": "assistant", "content": full})
