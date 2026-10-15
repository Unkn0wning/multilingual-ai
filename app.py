import streamlit as st
from groq import Groq
import base64
from urllib.parse import quote

st.set_page_config(page_title="JARVIS AI", page_icon="🤖")
st.title("🤖 JARVIS AI")
st.caption("By Hashir | Voice + Image Creator")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# === IMPORTANT: SINGLE MESSAGE LIST ===
if "messages" not in st.session_state:
    st.session_state.messages = []

if "first_message" not in st.session_state:
    st.session_state.first_message = True

# Show chat history - ONLY ONCE, NO LOOP
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if isinstance(m["content"], dict) and "image" in m["content"]:
            st.image(m["content"]["image"])
            st.caption(m["content"]["text"])
        else:
            st.markdown(m["content"])

# First welcome message - only once
if st.session_state.first_message:
    with st.chat_message("assistant"):
        st.markdown("Salam Hashir! I am **JARVIS** 🤖 Your personal AI by Hashir Ali. How can I help?")
    st.session_state.messages.append({"role": "assistant", "content": "Salam Hashir! I am **JARVIS** 🤖 Your personal AI by Hashir Ali. How can I help?"})
    st.session_state.first_message = False

def create_image(prompt):
    safe = quote(prompt)
    return f"https://image.pollinations.ai/prompt/{safe}?width=512&height=512&nologo=true"

# === TOP BAR: + and MIC ===
c1, c2 = st.columns(2)
with c1:
    with st.popover("＋ File / Picture"):
        up = st.file_uploader("Upload", type=["png","jpg","jpeg","pdf","txt"], key="jarvis_up")
        if up:
            st.success(up.name)
            if up.type.startswith("image"):
                st.image(up, width=150)
                st.session_state["last_img"] = base64.b64encode(up.getvalue()).decode()

with c2:
    with st.popover("🎤 Voice"):
        aud = st.audio_input("Voice", key="jarvis_voice")
        if aud:
            with st.spinner("Listening..."):
                try:
                    t = client.audio.transcriptions.create(
                        file=("v.wav", aud.getvalue()),
                        model="whisper-large-v3",
                        response_format="text"
                    )
                    st.success(f"You: {t}")
                    st.session_state["voice_text"] = t
                except Exception as e:
                    st.error(str(e))

# === CHAT INPUT - SINGLE ENTRY, NO DUPLICATE ===
prompt = st.chat_input("Ask JARVIS anything...")

# If voice was used
if "voice_text" in st.session_state:
    prompt = st.session_state.pop("voice_text")

if prompt:
    # 1. Add user message ONCE
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Check if image creation needed
    low = prompt.lower()
    is_image = any(x in low for x in ["create image", "generate image", "make image", "tasveer banao", "image banao", "draw", "picture banao", "create picture"])

    with st.chat_message("assistant"):
        if is_image:
            # IMAGE CREATE MODE
            with st.spinner("JARVIS creating image... 🎨"):
                clean_prompt = prompt.replace("create image", "").replace("generate image", "").replace("tasveer banao", "").strip()
                if clean_prompt == "":
                    clean_prompt = prompt
                url = create_image(clean_prompt)
                st.image(url, caption=clean_prompt)
                st.link_button("Download", url)
                answer = {"image": url, "text": f"JARVIS created: {clean_prompt}"}
                st.session_state.messages.append({"role": "assistant", "content": answer})
        else:
            # NORMAL ANSWER MODE - FIXED NAME = JARVIS
            full = ""
            box = st.empty()
            system_prompt = {
                "role": "system",
                "content": "Your name is JARVIS. You are JARVIS created by Hashir Ali. NEVER say your name is Hashir Ali AI. Always say: My name is JARVIS, created by Hashir Ali. You are helpful assistant. Answer in same language as user (Urdu if user speaks Urdu, English if English). Answer only ONCE, never repeat. Be concise."
            }
            msgs = [system_prompt] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages if isinstance(m["content"], str)]

            stream = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=msgs,
                stream=True
            )
            for ch in stream:
                if ch.choices[0].delta.content:
                    full += ch.choices[0].delta.content
                    box.markdown(full + "▌")
            box.markdown(full)
            # Add assistant answer ONCE
            st.session_state.messages.append({"role": "assistant", "content": full})
