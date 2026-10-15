import streamlit as st
from groq import Groq

st.set_page_config(page_title="Hashir Ali AI", page_icon="👑")
st.title("👑 Hashir Ali AI")
st.caption("🟢 Online | New 2026 Model | Multilingual")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY in Secrets!")
    st.stop()

# LANGUAGE SYSTEM - This fixes language!
SYSTEM_PROMPT = {
    "role": "system",
    "content": """You are Hashir Ali AI, made by Hashir Ali from Peshawar.
    RULES FOR LANGUAGE:
    - If user speaks English, reply in English.
    - If user speaks Urdu, reply in Urdu.
    - If user speaks Pashto, reply in Pashto.
    - If user speaks Hindi, reply in Hindi.
    - Default language is English.
    - Always be friendly, helpful, and answer like Meta AI.
    - Keep answers short and clear."""
}

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Salam Hashir! 👑 I am ready! Speak in English, Urdu, Pashto - I will reply in same language!"}]

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
        # Add system prompt to fix language
        all_messages = [SYSTEM_PROMPT] + st.session_state.messages
        stream = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=all_messages,
            stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full += chunk.choices[0].delta.content
                box.markdown(full + "▌")
        box.markdown(full)
        st.session_state.messages.append({"role": "assistant", "content": full})
