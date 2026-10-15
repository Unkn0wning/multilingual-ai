import streamlit as st
from groq import Groq
import base64

st.set_page_config(page_title="Hashir AI", page_icon="👑")

st.title("👑 Hashir Ali AI")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Salam! Type below 👇"}]

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"] if isinstance(m["content"], str) else "Image")

# === LEFT + and RIGHT MIC ===
c1, c2, c3 = st.columns([1, 5, 1])
with c1:
    with st.popover("＋"):
        up = st.file_uploader("File", type=["png","jpg","pdf","txt"], key="up")
        if up:
            st.success(up.name)

with c2:
    st.write("Type in middle box below 👇")

with c3:
    with st.popover("🎤"):
        aud = st.audio_input("Voice", key="aud")
        if aud:
            t = client.audio.transcriptions.create(file=("v.wav", aud.getvalue()), model="whisper-large-v3", response_format="text")
            st.session_state["voice"] = t
            st.success(t)

# === MAIN ENTRY - HERE YOU TYPE ===
prompt = st.chat_input("Type a message here...")

if "voice" in st.session_state:
    prompt = st.session_state.pop("voice")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        full = ""
        box = st.empty()
        stream = client.chat.completions.create(model="openai/gpt-oss-20b", messages=[{"role": "system", "content": "You are Hashir Ali AI"}] + st.session_state.messages, stream=True)
        for ch in stream:
            if ch.choices[0].delta.content:
                full += ch.choices[0].delta.content
                box.markdown(full + "▌")
        box.markdown(full)
        st.session_state.messages.append({"role": "assistant", "content": full})
        st.rerun()
