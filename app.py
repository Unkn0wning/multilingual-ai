import streamlit as st
from groq import Groq
import base64
from urllib.parse import quote

st.set_page_config(page_title="JARVIS AI", page_icon="🤖")
st.title("🤖 JARVIS AI")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "I am JARVIS by Hashir!"}]
if "pending_image" not in st.session_state:
    st.session_state.pending_image = None

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if isinstance(m["content"], dict):
            st.image(m["content"]["image"], width=300)
            st.write(m["content"]["text"])
        else:
            st.write(m["content"])

def make_url(p):
    return "https://image.pollinations.ai/prompt/" + quote(p) + "?width=512&height=512&nologo=true"

st.divider()
c1, c2, c3 = st.columns([1, 7, 1])

with c1:
    with st.popover("＋", use_container_width=True):
        up = st.file_uploader("Upload", type=["png","jpg","jpeg"], label_visibility="collapsed", key="plus")
        if up:
            st.image(up, width=150)
            st.session_state.pending_image = base64.b64encode(up.getvalue()).decode()
            st.success("Attached!")
            cap = st.text_input("What to do?", placeholder="make more robotic", key="cap")
            if cap:
                st.session_state.pending_caption = cap

with c2:
    chat_text = st.text_input("chat", placeholder="Ask JARVIS anything...", label_visibility="collapsed", key="main_input")

with c3:
    with st.popover("🎤", use_container_width=True):
        aud = st.audio_input("Voice", label_visibility="collapsed", key="mic")
        if aud:
            t = client.audio.transcriptions.create(file=("v.wav", aud.getvalue()), model="whisper-large-v3", response_format="text")
            st.session_state["voice"] = t

send = st.button("Send ➤")

final_prompt = None
if send and st.session_state.get("main_input"):
    final_prompt = st.session_state["main_input"]
if "voice" in st.session_state:
    final_prompt = st.session_state.pop("voice")
if st.session_state.get("trigger_create"):
    final_prompt = st.session_state.get("pending_caption", "")

if final_prompt:
    # === FIX: CLEAR THE BOX IMMEDIATELY ===
    st.session_state["main_input"] = ""
    st.session_state["cap"] = ""

    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        if st.session_state.pending_image:
            st.image(base64.b64decode(st.session_state.pending_image), width=150)
        st.write(final_prompt)
    with st.chat_message("assistant"):
        low = final_prompt.lower()
        want_image = True if st.session_state.pending_image else any(w in low for w in ["robotic","image","picture","banao","iron man"])
        if want_image and st.session_state.pending_image:
            with st.spinner("Creating..."):
                try:
                    v = client.chat.completions.create(model="meta-llama/llama-4-scout-17b-16e-instruct", messages=[{"role": "user", "content": [{"type": "text", "text": "Describe"}, {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + st.session_state.pending_image}}]}])
                    full_p = v.choices[0].message.content + ", " + final_prompt
                except:
                    full_p = final_prompt
                url = make_url(full_p)
                st.image(url)
                st.link_button("Download", url)
                st.session_state.messages.append({"role": "assistant", "content": {"image": url, "text": full_p}})
                st.session_state.pending_image = None
        elif want_image:
            url = make_url(final_prompt)
            st.image(url)
            st.session_state.messages.append({"role": "assistant", "content": {"image": url, "text": final_prompt}})
        else:
            full = ""
            box = st.empty()
            msgs = [{"role": "system", "content": "You are JARVIS by Hashir."}] + [m for m in st.session_state.messages if isinstance(m["content"], str)]
            s = client.chat.completions.create(model="openai/gpt-oss-20b", messages=msgs, stream=True)
            for ch in s:
                if ch.choices[0].delta.content:
                    full += ch.choices[0].delta.content
                    box.write(full + "_")
            box.write(full)
            st.session_state.messages.append({"role": "assistant", "content": full})
    st.rerun()
