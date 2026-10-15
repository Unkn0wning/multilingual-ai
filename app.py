import streamlit as st
from groq import Groq
import base64
from urllib.parse import quote

st.set_page_config(page_title="JARVIS AI", page_icon="🤖")
st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
.stApp {background-color: #0e1117;}
div[data-testid="stChatInput"] {background: #202c33; border-radius: 25px;}
.bottom-bar {display: flex; align-items: center; gap: 8px; background: #202c33; padding: 10px; border-radius: 30px; margin-top: 20px;}
</style>
""", unsafe_allow_html=True)

st.title("🤖 JARVIS AI")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "I am JARVIS by Hashir! Use + to upload, type to chat, mic to hold and ask!"}]
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

# ==== BOTTOM WHATSAPP BAR: + | INPUT | MIC HOLD ====
st.divider()
c1, c2, c3 = st.columns([1, 7, 1])

with c1:
    with st.popover("＋", use_container_width=True):
        st.write("Upload Picture")
        up = st.file_uploader("Upload", type=["png","jpg","jpeg"], label_visibility="collapsed", key="plus_inside")
        if up:
            st.image(up, width=150)
            st.session_state.pending_image = base64.b64encode(up.getvalue()).decode()
            st.success("Picture attached! Now type what to do below")

with c2:
    # This is your "Ask JARVIS anything..." - NOW WITH + AND MIC AROUND IT
    chat_text = st.text_input("chat", placeholder="Ask JARVIS anything... + for picture, hold mic for voice", label_visibility="collapsed", key="main_chat_text")

with c3:
    with st.popover("🎤", use_container_width=True):
        st.write("Hold to Ask - Click to record")
        aud = st.audio_input("Hold to talk", label_visibility="collapsed", key="mic_hold")
        if aud:
            try:
                t = client.audio.transcriptions.create(file=("v.wav", aud.getvalue()), model="whisper-large-v3", response_format="text")
                st.success("You: " + t)
                st.session_state["hold_voice"] = t
            except Exception as e:
                st.error(str(e))

# SEND BUTTONS
send_col1, send_col2 = st.columns([1, 5])
with send_col1:
    send_clicked = st.button("Send ➤", use_container_width=True)

# Handle sending
final_prompt = None
if send_clicked and chat_text:
    final_prompt = chat_text
if "hold_voice" in st.session_state:
    final_prompt = st.session_state.pop("hold_voice")

if final_prompt:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        if st.session_state.pending_image:
            st.image(base64.b64decode(st.session_state.pending_image), width=150)
            st.caption("Attached picture")
        st.write(final_prompt)

    # Decide if image creation
    with st.chat_message("assistant"):
        low = final_prompt.lower()
        want_image = any(w in low for w in ["robotic", "iron man", "create image", "make image", "banao", "edit", "picture"])

        if want_image and st.session_state.pending_image:
            with st.spinner("JARVIS creating..."):
                try:
                    v = client.chat.completions.create(model="meta-llama/llama-4-scout-17b-16e-instruct", messages=[{"role": "user", "content": [{"type": "text", "text": "Describe this person for edit"}, {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + st.session_state.pending_image}}]}])
                    base_desc = v.choices[0].message.content
                    full_prompt = base_desc + ", " + final_prompt + ", ultra detailed, 8k"
                except:
                    full_prompt = final_prompt
                url = make_url(full_prompt)
                st.image(url, caption="JARVIS Created")
                st.link_button("Download", url)
                st.session_state.messages.append({"role": "assistant", "content": {"image": url, "text": "Created: " + final_prompt}})
                st.session_state.pending_image = None
        elif want_image:
            url = make_url(final_prompt)
            st.image(url)
            st.link_button("Download", url)
            st.session_state.messages.append({"role": "assistant", "content": {"image": url, "text": final_prompt}})
        else:
            # Normal JARVIS answer
            full = ""
            box = st.empty()
            msgs = [{"role": "system", "content": "You are JARVIS by Hashir Ali. Name is JARVIS. Answer once, same language."}]
            for x in st.session_state.messages:
                if isinstance(x["content"], str):
                    msgs.append(x)
            s = client.chat.completions.create(model="openai/gpt-oss-20b", messages=msgs, stream=True)
            for ch in s:
                if ch.choices[0].delta.content:
                    full = full + ch.choices[0].delta.content
                    box.write(full + "_")
            box.write(full)
            st.session_state.messages.append({"role": "assistant", "content": full})
    st.rerun()
