import streamlit as st
from groq import Groq
import base64
from urllib.parse import quote

st.set_page_config(page_title="JARVIS AI", page_icon="robot")
st.title("JARVIS AI")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []
if "first" not in st.session_state:
    st.session_state.first = True

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if isinstance(m["content"], dict):
            if "image" in m["content"]:
                st.image(m["content"]["image"], width=300)
                st.markdown(m["content"]["text"])
        else:
            st.markdown(m["content"])

if st.session_state.first:
    with st.chat_message("assistant"):
        st.markdown("I am JARVIS by Hashir! Upload picture + write what to do")
    st.session_state.messages.append({"role": "assistant", "content": "I am JARVIS by Hashir!"})
    st.session_state.first = False

def make_image_url(prompt_text):
    safe = quote(prompt_text)
    url = "https://image.pollinations.ai/prompt/" + safe + "?width=512&height=512&nologo=true"
    return url

st.divider()
st.subheader("Upload + Instruction")

up_file = st.file_uploader("Upload Picture", type=["png","jpg","jpeg"], key="upload1")
if up_file:
    st.image(up_file, width=200)

text_instruction = st.text_input("What to do with this picture?", placeholder="make it more robotic, iron man suit", key="inst1")

if st.button("Create Picture"):
    if text_instruction:
        final_prompt = text_instruction
        if up_file:
            b64 = base64.b64encode(up_file.getvalue()).decode()
            try:
                vis = client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    messages=[{"role": "user", "content": [{"type": "text", "text": "Describe this person for image creation"}, {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64}}]}]
                )
                desc = vis.choices[0].message.content
                final_prompt = desc + ", " + text_instruction
            except:
                final_prompt = text_instruction

        url = make_image_url(final_prompt)
        st.session_state.messages.append({"role": "user", "content": text_instruction})
        with st.chat_message("user"):
            if up_file:
                st.image(up_file, width=150)
            st.markdown(text_instruction)
        with st.chat_message("assistant"):
            st.image(url)
            st.link_button("Download", url)
        st.session_state.messages.append({"role": "assistant", "content": {"image": url, "text": final_prompt}})

st.divider()
with st.popover("Voice - Ask JARVIS"):
    aud = st.audio_input("Voice", key="voice1")
    if aud:
        try:
            t = client.audio.transcriptions.create(file=("v.wav", aud.getvalue()), model="whisper-large-v3", response_format="text")
            st.success("You said: " + t)
            st.session_state["voice_text"] = t
        except Exception as e:
            st.error(str(e))

prompt = st.chat_input("Ask JARVIS anything...")

if "voice_text" in st.session_state:
    prompt = st.session_state.pop("voice_text")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        full = ""
        box = st.empty()
        system_msg = {"role": "system", "content": "You are JARVIS created by Hashir Ali. Your name is JARVIS. Never say Hashir AI. Answer once, same language as user."}
        msgs = [system_msg]
        for x in st.session_state.messages:
            if isinstance(x["content"], str):
                msgs.append(x)
        stream = client.chat.completions.create(model="openai/gpt-oss-20b", messages=msgs, stream=True)
        for ch in stream:
            if ch.choices[0].delta.content:
                full += ch.choices[0].delta.content
                box.markdown(full + "_")
        box.markdown(full)
        st.session_state.messages.append({"role": "assistant", "content": full})
