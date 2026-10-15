import streamlit as st
from groq import Groq

st.set_page_config(page_title="Hashir Ali AI", page_icon="👑")
st.title("👑 Hashir Ali AI")
st.caption("🟢 Online | New 2026 Model")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY in Streamlit Secrets!")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Salam Hashir! 👑 I am updated to new 2026 model - ready!"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Type a message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        full = ""
        box = st.empty()
        stream = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=st.session_state.messages,
            stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full += chunk.choices[0].delta.content
                box.markdown(full + "▌")
        box.markdown(full)
        st.session_state.messages.append({"role": "assistant", "content": full})
