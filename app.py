import streamlit as st
from groq import Groq

st.set_page_config(page_title="Hashir AI", page_icon="👑")
st.title("Hashir Ali AI")
st.caption("Online WhatsApp Style")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

prompt = st.chat_input("Type a message...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        full = ""
        box = st.empty()
        s = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=st.session_state.messages,
            stream=True
        )
        for c in s:
            if c.choices[0].delta.content:
                full += c.choices[0].delta.content
                box.markdown(full)
        box.markdown(full)
        st.session_state.messages.append({"role": "assistant", "content": full})
