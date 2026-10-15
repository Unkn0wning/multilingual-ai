import streamlit as st
from groq import Groq
import base64
import requests
from urllib.parse import quote

st.set_page_config(page_title="Hashir AI", page_icon="👑")
st.title("👑 Hashir Ali AI")
st.caption("Chat + Voice Answer + Image Create/Edit")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Salam Hashir! 👑 Now fixed: Voice will ANSWER, and I can CREATE pictures! Try: 'Create a picture of cat' or Voice 'Peshawar ka mausam kaisa hai'"}]

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if isinstance(m["content"], dict) and "image" in m["content"]:
            st.image(m["content"]["image"])
            st.markdown(m["content"]["text"])
        else:
            st.markdown(m["content"] if isinstance(m["content"], str) else str(m["content"]))

def create_image_from_text(prompt):
    # Free image generator - no API key needed
    safe_prompt = quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=512&height=512&nologo=true"
    return url

# === LEFT + AND RIGHT MIC ===
c1, c2, c3 = st.columns([1, 5, 1])
with c1:
    with st.popover("＋"):
        up = st.file_uploader("Upload", type=["png","jpg","jpeg","pdf","txt"], key="up_plus")
        if up:
            st.success(up.name)
            if up.type.startswith("image"):
                st.image(up, width=120)
                b64 = base64.b64encode(up.getvalue()).decode()
                st.session_state["last_image_b64"] = b64
                st.session_state["last_image_name"] = up.name

with c2:
    st.write("")

with c3:
    with st.popover("🎤"):
        aud = st.audio_input("Voice", key="mic_main")
        if aud:
            with st.spinner("AI is listening and understanding..."):
                try:
                    # Transcribe
                    transcribed = client.audio.transcriptions.create(
                        file=("voice.wav", aud.getvalue()),
                        model="whisper-large-v3",
                        response_format="text"
                    )
                    st.success(f"You said: {transcribed}")
                    # NOW IT WILL ANSWER, NOT JUST TRANSLATE
                    st.session_state["voice_prompt"] = transcribed
                except Exception as e:
                    st.error(str(e))

# === MAIN INPUT ===
prompt = st.chat_input("Type or say: 'Create image of...' / 'Edit my picture'")

# Voice override
if "voice_prompt" in st.session_state:
    prompt = st.session_state.pop("voice_prompt")

if prompt:
    # Check if user wants to CREATE image
    lower_prompt = prompt.lower()
    is_image_request = any(word in lower_prompt for word in ["create image", "generate image", "make image", "picture banao", "image banao", "tasveer banao", "create a picture", "generate a picture", "draw", "bana do image"])

    is_edit_request = any(word in lower_prompt for word in ["edit", "change", "modify", "background", "edit my picture"]) and "last_image_b64" in st.session_state

    if is_image_request or is_edit_request:
        # CREATE / EDIT IMAGE
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            if is_edit_request and "last_image_b64" in st.session_state:
                st.image(base64.b64decode(st.session_state["last_image_b64"]), width=200)
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Creating picture... 🎨"):
                # If edit request, combine original + new prompt
                if is_edit_request:
                    final_prompt = f"{prompt}, edit from uploaded image"
                else:
                    final_prompt = prompt.replace("create image", "").replace("generate image", "").replace("make image", "").strip()
                    if final_prompt == "":
                        final_prompt = prompt

                img_url = create_image_from_text(final_prompt)
                try:
                    # Try to load image
                    st.image(img_url, caption=f"Created: {final_prompt}")
                    st.markdown(f"Here is your picture! 👇 Created from: **{prompt}**")
                    st.session_state.messages.append({"role": "assistant", "content": {"image": img_url, "text": f"Created picture for: {prompt}"}})
                    # Download button
                    st.link_button("Download Picture", img_url)
                except Exception as e:
                    st.error(f"Image error: {e}")
                    st.markdown(f"Image link: {img_url}")
    else:
        # NORMAL CHAT + VOICE QUESTION ANSWERING
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            full = ""
            box = st.empty()
            # System prompt that FIXES voice translation issue
            system = {
                "role": "system",
                "content": "You are Hashir Ali AI. User may speak via voice transcription. Your job is to ANSWER their question, not just translate or repeat what they said. If they ask 'Peshawar ka mausam kaisa hai' answer about weather. If voice says 'hello' reply hello. Always answer helpfully. Reply in same language as user. Default English."
            }
            all_msgs = [system] + [m for m in st.session_state.messages if isinstance(m.get("content"), str)]
            stream = client.chat.completions.create(model="openai/gpt-oss-20b", messages=all_msgs, stream=True)
            for ch in stream:
                if ch.choices[0].delta.content:
                    full += ch.choices[0].delta.content
                    box.markdown(full + "▌")
            box.markdown(full)
            st.session_state.messages.append({"role": "assistant", "content": full})

    st.rerun()
