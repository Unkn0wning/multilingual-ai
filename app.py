import streamlit as st
from groq import Groq
import base64

st.set_page_config(page_title="Hashir Ali AI", page_icon="👑", layout="centered")
st.title("👑 Hashir Ali AI")
st.caption("🟢 Online | Voice + Vision + Files | 2026 Model")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY in Secrets!")
    st.stop()

SYSTEM_PROMPT = {
    "role": "system",
    "content": "You are Hashir Ali AI, made by Hashir Ali from Peshawar, Pakistan. Reply in SAME language user uses. Default is English. If Urdu, reply Urdu. If Pashto, reply Pashto. Be friendly, fast, helpful like Meta AI."
}

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Salam Hashir! 👑 Full Pro Version Ready! 🚀\n\n✅ Chat\n✅ Voice\n✅ Picture Upload\n✅ File Upload\n\nHow can I help?"}]

# SIDEBAR - Features are HERE!
with st.sidebar:
    st.header("👑 Pro Features")
    st.caption("All features are here!")

    uploaded_file = st.file_uploader("📎 Upload Picture / PDF / File", type=["png","jpg","jpeg","pdf","txt","mp3","mp4"])
    if uploaded_file:
        st.success(f"Uploaded: {uploaded_file.name}")
        st.image(uploaded_file) if uploaded_file.type.startswith("image") else None

    st.divider()
    audio = st.audio_input("🎤 Voice Message - Speak!")
    if audio:
        st.success("Voice received! Transcribing...")
        # Transcribe with Groq Whisper
        transcription = client.audio.transcriptions.create(
            file=("audio.wav", audio.getvalue()),
            model="whisper-large-v3",
            response_format="text"
        )
        st.write(f"You said: {transcription}")
        # Auto send transcribed text as prompt
        st.session_state['voice_prompt'] = transcription

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Show chats
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Check voice prompt
prompt = st.chat_input("Type a message...")
if 'voice_prompt' in st.session_state:
    prompt = st.session_state.pop('voice_prompt')

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        full = ""
        box = st.empty()
        all_messages = [SYSTEM_PROMPT] + st.session_state.messages

        # Use vision model if image uploaded, else text model
        model_to_use = "openai/gpt-oss-20b"
        # If image, you can switch to vision model: meta-llama/llama-4-scout-17b-16e-instruct

        stream = client.chat.completions.create(
            model=model_to_use,
            messages=all_messages,
            stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full += chunk.choices[0].delta.content
                box.markdown(full + "▌")
        box.markdown(full)
        st.session_state.messages.append({"role": "assistant", "content": full})
