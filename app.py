import streamlit as st
from groq import Groq

st.set_page_config(page_title="Hashir Ali AI", page_icon="👑", layout="centered")

st.markdown("""
<style>
.stChatMessage {border-radius: 20px; padding: 12px;}
#MainMenu, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("👑 Hashir Ali AI")
st.caption("🟢 Online | Super Fast like Meta AI | WhatsApp Style")

# Connect to Groq
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("⚠️ Please add GROQ_API_KEY in Streamlit Secrets!")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Salam Hashir! 👑 I am your Hashir Ali AI - Now 10x faster like Meta AI! How can I help you today?"}]

# Show chat
for msg in st.session_state.messages:
    avatar = "👑" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Chat Input
if prompt := st.chat_input("Type a message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="👑"):
        placeholder = st.empty()
        full_response = ""
        try:
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages,
                temperature=0.7,
                max_tokens=1024,
                stream=True,
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
        except Exception as e:
            placeholder.markdown(f"Error: {e}")

    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Sidebar Options - Like WhatsApp
with st.sidebar:
    st.header("👑 Hashir AI Options")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.file_uploader("📎 Upload File", type=["pdf","png","jpg","txt"])
    st.audio_input("🎤 Voice Message")
    st.divider()
    st.caption("Made by Hashir Ali 👑")
    st.caption("Fast | WhatsApp Style | Meta AI Level")
