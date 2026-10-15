import streamlit as st
from groq import Groq
import base64

st.set_page_config(page_title="Hashir AI", page_icon="👑", layout="centered")

st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
.stApp {background-color: #111b21;}
h1, p {color: white!important;}
</style>
""", unsafe_allow_html=True)

st.title("👑 Hashir Ali AI")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Salam Hashir! 👑 Fixed version! No error now!"}]

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"] if isinstance(m["content"], str) else "Picture")

# ==== FIXED BOTTOM BAR ====
c1, c2, c3 = st.columns([1, 5, 1])

prompt_final = None
image_b64 = None

with c1:
    with st.popover("＋"):
        up = st.file_uploader("Upload", type=["png","jpg","jpeg","pdf","txt"], label_visibility="collapsed", key="plus_up")
        if up:
            st.success(up.name)
            if up.type.startswith("image"):
                st.image(up, width=120)
                image_b64 = base64.b64encode(up.getvalue()).decode()
                prompt_final = f"Describe this picture {up.name}"
            else:
                try:
                    txt_content = up.getvalue().decode()[:1500]
                    prompt_final = f"File {up.name}: {txt_content}"
                except:
                    prompt_final = f"I uploaded {up.name}"

with c2:
    user_text = st.text_input("type", placeholder="Type a message", label_visibility="collapsed", key="user_txt")

with c3:
    with st.popover("🎤"):
        aud = st.audio_input("Voice", label_visibility="collapsed", key="mic_voice")
        if aud:
            with st.spinner("Listening..."):
                try:
                    t = client.audio.transcriptions.create(
                        file=("v.wav", aud.getvalue()),
                        model="whisper-large-v3",
                        response_format="text"
                    )
                    st.success(f"You: {t}")
                    prompt_final = t
                except Exception as e:
                    st.error(str(e))

# Send logic
