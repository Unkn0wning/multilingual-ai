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
if "pending_caption" not in st.session_state:
    st.session_state.pending_caption = ""

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
        st.write("Upload Picture")
        up = st.file_uploader("Upload", type=["png","jpg","jpeg"], label_visibility="collapsed", key="plus_final")
        if up:
            st.image(up, width=200)
            st.session_state.pending_image = base64.b64encode(up.getvalue()).decode()
            st.success("Attached!")

            # === NEW: TYPING SPACE WITH PICTURE - LIKE YOU ASKED! ===
            st.write("---")
            caption = st.text_input("Write what to do with this picture:", placeholder="make it more robotic, iron man suit, glowing", key="pic_caption")
            if caption:
                st.session_state.pending_caption = caption
                st.info(f"Instruction: {caption}")

            if st.button("Create with this picture ➤", use_container_width=True):
                if st.session_state.pending_caption == "":
                    st.warning("Please write instruction above first!")
                else:
                    st.session_state["trigger_create"] = True

with c2:
    # CLEAN - Only this text
    chat_text = st.text_input("chat", placeholder="Ask JARVIS anything...", label_visibility="collapsed", key="main_clean")

with c3:
    with st.popover("🎤", use_container_width=True):
        aud = st.audio_input("Voice", label_visibility="collapsed", key="mic_final")
        if aud:
            t = client.audio.transcriptions.create(file=("v.wav", aud.getvalue()), model="whisper-large-v3", response_format="text")
            st.session_state["voice"] = t

send_main = st.button("Send ➤")

# Handle all sends
final_prompt = None
trigger_from_pic = st.session_state.pop("trigger_create", False)

if trigger_from_pic and st.session_state.pending_caption:
    final_prompt = st.session_state.pending_caption
elif send_main and chat_text:
    final_prompt = chat_text
elif "voice" in st.session_state:
    final_prompt = st.session_state.pop("voice")

if final_prompt:
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        if st.session_state.pending_image:
            st.image(base64.b64decode(st.session_state.pending_image), width=150)
        st.write(final_prompt)
    with st.chat_message("assistant"):
        low = final_prompt.lower()
        want_image = True if st.session_state.pending_image else any(w in low for w in ["robotic", "create image", "make image", "banao", "edit", "picture", "iron man"])

        if want_image and st.session_state.pending_image:
            with st.spinner("JARVIS editing your picture..."):
                try:
                    v = client.chat.completions.create(model="meta-llama/llama-4-scout-17b-16e-instruct", messages=[{"role": "user", "content": [{"type": "text", "text": "Describe this person briefly for image generation"}, {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + st.session_state.pending_image}}]}])
                    full_p = v.choices[0].message.content + ", " + final_prompt + ", ultra detailed, 8k"
                except:
                    full_p = final_prompt
                url = make_url(full_p)
                st.image(url, caption="JARVIS Created")
                st.link_button("Download Picture", url)
                st.session_state.messages.append({"role": "assistant", "content": {"image": url, "text": full_p}})
                st.session_state.pending_image = None
                st.session_state.pending_caption = ""
        elif want_image:
            url = make_url(final_prompt)
            st.image(url)
            st.link_button("Download", url)
            st.session_state.messages.append({"role": "assistant", "content": {"image": url, "text": final_prompt}})
        else:
            full = ""
            box = st.empty()
            msgs = [{"role": "system", "content": "You are JARVIS by Hashir Ali. Name is JARVIS. Answer once."}] + [m for m in st.session_state.messages if isinstance(m["content"], str)]
            s = client.chat.completions.create(model="openai/gpt-oss-20b", messages=msgs, stream=True)
            for ch in s:
                if ch.choices[0].delta.content:
                    full += ch.choices[0].delta.content
                    box.write(full + "_")
            box.write(full)
            st.session_state.messages.append({"role": "assistant", "content": full})
    st.rerun()
