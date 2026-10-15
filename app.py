import streamlit as st
from groq import Groq
import base64

st.set_page_config(page_title="Hashir AI", page_icon="👑", layout="centered")

# WhatsApp Dark
st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
.stApp {background-color: #111b21;}
h1, p {color: white!important;}
.stTextInput input {background: #2a3942!important; color: white!important; border-radius: 25px!important; border: none!important; padding: 12px 16px!important;}
.stButton button {border-radius: 50%!important; height: 45px; width: 45px; background: #202c33!important; border: none!important; font-size: 20px;}
div[data-testid="column"] {display: flex; align-items: center; justify-content: center;}
</style>
""", unsafe_allow_html=True)

st.title("👑 Hashir Ali AI")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Salam Hashir! 👑 WhatsApp Layout Ready! Left + for files, Right Mic for voice!"}]

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if isinstance(m["content"], str):
            st.markdown(m["content"])
        else:
            st.markdown("Picture message")

# ==== WHATSAPP BOTTOM BAR - LEFT + MIDDLE RIGHT MIC ====
st.markdown("<br><br>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([1, 6, 1])

prompt_from_anywhere = None

with c1:
    with st.popover("＋", use_container_width=True):
        st.write("Upload File")
        up_file = st.file_uploader("Choose", type=["png","jpg","jpeg","pdf","txt"], label_visibility="collapsed", key="left_plus")
        if up_file:
            st.success(up_file.name)
            if up_file.type.startswith("image"):
                st.image(up_file, width=150)
                # Prepare for AI vision
                b64 = base64.b64encode(up_file.getvalue()).decode()
                st.session_state["pending_image"] = b64
                prompt_from_anywhere = f"I uploaded picture {up_file.name}. What is in it?"
            else:
                # For pdf/txt
                try:
                    content = up_file.getvalue().decode()
                    prompt_from_anywhere = f"I uploaded file {up_file.name}. Content: {content[:2000]}"
                except:
                    prompt_from_anywhere = f"I uploaded file {up_file.name}. Please help me with it."

with c2:
    txt = st.text_input("msg", placeholder="Type a message", label_visibility="collapsed", key="main_input")

with c3:
    with st.popover("🎤", use_container_width=True):
        st.write("Voice Command")
        aud = st.audio_input("Record", label_visibility="collapsed", key="right_mic")
        if aud:
            st.audio(aud)
            with st.spinner("Listening..."):
                try:
                    t = client.audio.transcriptions.create(
                        file=("voice.wav", aud.getvalue()),
                        model="whisper-large-v3",
                        response_format="text"
                    )
                    st.success(f"You said: {t}")
                    prompt_from_anywhere = t
                except Exception as e:
                    st.error(f"Error: {e}")

# Text send logic
if txt:
    # When user presses Enter in text box, we need a send button
    if st.session_state.get("main_input"):
        prompt_from_anywhere = txt

# Extra send button below text for mobile Enter issue
if st.button("Send ➤", use_container_width=False):
    if txt:
        prompt_from_anywhere = txt

# ==== PROCESS ANY PROMPT ====
if prompt_from_anywhere:
    # Clear input
    st.session_state.messages.append({"role": "user", "content": prompt_from_anywhere})
    with st.chat_message("user"):
        if "pending_image" in st.session_state:
            st.image(base64.b64decode(st.session_state["pending_image"]), width=200)
        st.markdown(prompt_from_anywhere)

    with st.chat_message("assistant"):
        full = ""
        box = st.empty()

        # If image was uploaded, use vision model
        if "pending_image" in st.session_state:
            b64 = st.session_state.pop("pending_image")
            msgs = [
                {"role": "user", "content": [
                    {"type": "text", "text": prompt_from_anywhere},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]}
            ]
            try:
                s = client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    messages=msgs,
                    stream=True
                )
            except:
                s = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[{"role": "user", "content": prompt_from_anywhere}],
                    stream=True
                )
        else:
            # Normal text / voice / file
            all_msgs = [{"role": "system", "content": "You are Hashir Ali AI. Reply same language as user."}] + [m for m in st.session_state.messages if isinstance(m["content"], str)]
            s = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=all_msgs,
                stream=True
            )

        for ch in s:
            if ch.choices[0].delta.content:
                full += ch.choices[0].delta.content
                box.markdown(full + "▌")
        box.markdown(full)
        st.session_state.messages.append({"role": "assistant", "content": full})

    # Clear text box
    st.session_state["main_input"] = ""
    st.rerun()
