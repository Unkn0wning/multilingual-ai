import streamlit as st
from groq import Groq
import base64
from urllib.parse import quote

st.set_page_config(page_title="JARVIS", page_icon="🤖")
st.title("🤖 JARVIS AI")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []
if "first" not in st.session_state:
    st.session_state.first = True

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if isinstance(m["content"], dict) and "image" in m["content"]:
            st.image(m["content"]["image"], width=300)
            st.markdown(m["content"]["text"])
        else:
            st.markdown(m["content"])

if st.session_state.first:
    with st.chat_message("assistant"):
        st.markdown("I am **JARVIS** by Hashir! Upload pic + tell me what to do - like 'make it more robotic'")
    st.session_state.messages.append({"role": "assistant", "content": "I am JARVIS by Hashir! Upload pic + tell me what to do"})
    st.session_state.first = False

def make_image(prompt):
    return f"https://image.pollinations.ai/prompt/{quote(prompt)}?width=512&height=512&nologo=true&seed={st.session_state.get('seed', 1)}"

# ==== NEW: UPLOAD + INSTRUCTION IN ONE PLACE ====
with
