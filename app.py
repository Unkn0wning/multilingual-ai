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
