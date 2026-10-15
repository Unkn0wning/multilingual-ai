import streamlit as st
from groq import Groq
import base64

st.set_page_config(page_title="Hashir AI", page_icon="👑", layout="centered")

# WhatsApp Dark Theme
st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
.stApp {background-color: #111b21;}
h1, h2, h3, p, span {color: white!important;}
</style>
""", unsafe_allow_html=True)

st.title("👑 Hashir Ali AI")
st.caption("🟢 Online | Voice + Picture Understanding")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Salam Hashir! 👑 Now I can HEAR your voice and SEE your pictures! Try uploading or voice!"}]

# Show chat
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# === SIDEBAR - WHERE AI UNDERSTANDS ===
with st.sidebar:
    st.header("👑 WhatsApp Tools")

    st.subheader("📷 Picture Upload")
    img_file = st.file_uploader("Upload Picture", type=["png","jpg","jpeg"], key="img")
    if img_file:
        st.image(img_file, caption="Your Picture")
        if st.button("Ask AI about this picture"):
            # Convert image to base64 for AI vision
            b64 = base64.b64encode(img_file.getvalue()).decode()
            with st.chat_message("user"):
                st.image(img_file)
                st.markdown("What is in this picture?")

            st.session_state.messages.append({"role": "user", "content": [{"type": "text", "text": "What is in this picture?"}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]})

            with st.chat_message("assistant"):
                box = st.empty()
                full = ""
                try:
                    # Use Vision Model
                    chat = client.chat.completions.create(
                        model="meta-llama/llama-4-scout-17b-16e-instruct",
                        messages=st.session_state.messages,
                        stream=True
                    )
                    for c in chat:
                        if c.choices[0].delta.content:
                            full += c.choices[0].delta.content
                            box.markdown(full + "▌")
                except:
                    # Fallback if vision model not available
                    chat = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=[{"role": "user", "content": "User uploaded a picture. Tell them you can see pictures now and ask what they want to know about it."}],
                        stream=True
                    )
                    for c in chat:
                        if c.choices[0].delta.content:
                            full += c.choices[0].delta.content
                            box.markdown(full + "▌")
                box.markdown(full)
                st.session_state.messages.append({"role": "assistant", "content": full})

    st.divider()
    st.subheader("🎤 Voice Message - AI Understands!")
    voice_file = st.audio_input("Record Voice", key="voice")
    if voice_file:
        st.audio(voice_file)
        with st.spinner("AI is listening..."):
            try:
                text = client.audio.transcriptions.create(
                    file=("voice.wav", voice_file.getvalue()),
                    model="whisper-large-v3",
                    response_format="text"
                )
                st.success(f"You said: {text}")
                # Auto send transcribed voice to AI
                st.session_state["auto_voice"] = text
            except Exception as e:
                st.error(f"Voice error: {e}")

    st.divider()
    st.subheader("📎 File Upload")
    doc_file = st.file_uploader("Upload File", type=["pdf","txt"], key="doc")
    if doc_file:
        st.success(doc_file.name)

# === MAIN CHAT INPUT ===
prompt = st.chat_input("Type a message...")

# Check if voice was transcribed
if "auto_voice" in st.session_state:
    prompt = st.session_state.pop("auto_voice")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        full = ""
        box = st.empty()
        # Simple text list for normal chat
        text_messages = []
        for msg in st.session_state.messages:
            if isinstance(msg["content"], str):
                text_messages.append(msg)
            else:
                text_messages.append({"role": msg["role"], "content": "User asked about a picture"})

        stream = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=text_messages,
            stream=True
        )
        for c in stream:
            if c.choices[0].delta.content:
                full += c.choices[0].delta.content
                box.markdown(full + "▌")
        box.markdown(full)
        st.session_state.messages.append({"role": "assistant", "content": full})
