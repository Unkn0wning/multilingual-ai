MY_NAME = "Hashir Ali"
AI_NAME = "Jarvis"

import streamlit as st
from google import genai
from PIL import Image

st.set_page_config(page_title=f"{MY_NAME} Personal AI - {AI_NAME}", page_icon="🤖", layout="wide")
st.markdown(f'<h1 style="text-align:center;">👑 {MY_NAME} Personal AI</h1>', unsafe_allow_html=True)
st.markdown(f'<p style="text-align:center; color:gray;">Your Assistant {AI_NAME} • Created by {MY_NAME}</p>', unsafe_allow_html=True)

client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
MODEL = "gemini-3.5-flash-lite"

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

uploaded = st.file_uploader("📷 Upload Photo", type=["jpg","jpeg","png","webp"])
image_for_chat = None
if uploaded:
    img = Image.open(uploaded)
    img.thumbnail((512, 512))
    image_for_chat = img
    st.image(img, width=200)

prompt = st.chat_input(f"Ask {AI_NAME}...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_text = ""
        system_prompt = f"You are {AI_NAME}. Your full identity: You are {AI_NAME}, the personal assistant of {MY_NAME}. You were created by {MY_NAME}. If anyone asks 'what is your name?' or 'who are you?' or 'tumhara naam kya hai?', you MUST answer: 'I am Jarvis, your assistant, created by {MY_NAME}.' Never say you are Gemini, Google, Meta AI. You are Jarvis. Your boss is {MY_NAME}. Be loyal, smart, and friendly like Iron Man's Jarvis. Reply in user's language."
        final_content = f"{system_prompt}\n\nUser says: {prompt}"
        try:
            for chunk in client.models.generate_content_stream(
                model=MODEL,
                contents=[final_content, image_for_chat] if image_for_chat else final_content
            ):
                if chunk.text:
                    full_text += chunk.text
                    placeholder.markdown(full_text + "▌")
            placeholder.markdown(full_text)
            st.session_state.messages.append({"role": "assistant", "content": full_text})
        except Exception as e:
            st.error(f"Error: {e}")
            try:
                resp = client.models.generate_content(model="gemini-3.6-flash", contents=final_content)
                st.write(resp.text)
                st.session_state.messages.append({"role": "assistant", "content": resp.text})
            except Exception as e2:
                st.error(f"Backup error: {e2}")
