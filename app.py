import streamlit as st
from groq import Groq

st.set_page_config(page_title="Hashir Ali AI", page_icon="👑", layout="centered")

st.markdown("""
<style>
.stChatMessage {border-radius: 18px; padding: 10px;}
#MainMenu, footer {visibility: hidden;}
.stChatInput {border-radius: 25px !important;}
</style>
""", unsafe_allow_html=True)

st.title("👑 Hashir Ali AI")
st.caption("🟢 Online | Super Fast like Meta AI | WhatsApp Style")

# Connect Groq
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("⚠️ Add GROQ_API_KEY in Streamlit Secrets!")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Salam Hashir! 👑 I am your Hashir Ali AI - Now 10x faster like Meta AI! How can I help you today?"}]

# Show old chats
for msg in st.session_state.messages:
    avatar = "👑" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Type a message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="👑"):
        placeholder = st.empty()
        full_response = ""
        try:
            stream = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=st.session_state.messages,
                temperature=0.7,
                max_tokens=2048,
                stream=True,
            )
            for chunk in stream:
