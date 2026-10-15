import streamlit as st
from groq import Groq
import base64
from urllib.parse import quote
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="JARVIS AI", page_icon="🤖")
st.title("🤖 JARVIS AI")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "I am JARVIS by Hashir!"}]
if "pending_image" not in st.session_state:
    st.session_state.pending_image = None
if "do_clear" not in st.session_state:
    st.session_state.do_clear = False
if "user_location" not in st.session_state:
    st.session_state.user_location = None

if st.session_state.do_clear:
    st.session_state.main_input = ""
    st.session_state.cap = ""
    st.session_state.do_clear = False

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if isinstance(m["content"], dict):
            if "image" in m["content"]:
                st.image(m["content"]["image"], width=300)
            if "map" in m["content"]:
                st.map(pd.DataFrame([m["content"]["map"]]))
                st.write(f"📍 {m['content']['text']}")
            else:
                if "image" not in m["content"]:
                    st.write(m["content"].get("text",""))
        else:
            st.write(m["content"])

def make_url(p):
    return "https://
