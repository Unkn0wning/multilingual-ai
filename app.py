import streamlit as st
from google import genai
from deep_translator import GoogleTranslator
from PIL import Image

st.set_page_config(page_title="Multilingual AI Pro", page_icon="🎤")

st.title("🎤📷 Multilingual AI Pro")
st.write("Voice + Picture + Video + Translate")

# Gemini client
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

# Sidebar - Google Translate Option
st.sidebar.header("🌐 Google Translate")
translate_on = st.sidebar.checkbox("Enable Translation")
target_lang = st.sidebar.selectbox("Translate to:", ["ur", "ps", "en", "ar"], index=0)

# 1. Voice Message Option
st.subheader("🎤 Voice Message")
audio = st.audio_input("Tap to record")
if audio:
    st.audio(audio)

# 2. Picture and Video Upload Option
st.subheader("🖼️ Upload Picture / Video")
uploaded = st.file_uploader("Choose file", type=["jpg","jpeg","png","mp4","mov","mp3","wav","m4a"])

image_to_send = None
if uploaded:
    if uploaded.type.startswith("image"):
        image_to_send = Image.open(uploaded)
        st.image(image_to_send, caption="Uploaded Image")
    elif uploaded.type.startswith("video"):
        st.video(uploaded)
    else:
        st.audio(uploaded)

# 3. Text Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_text = st.chat_input("Type salam / sta tso khpal hal waya / or ask about photo...")

# Combine prompt
final_prompt = None
if user_text:
    final_prompt = user_text
elif uploaded and not user_text:
    final_prompt = "Explain this image/video in English, Urdu and Pashto"
elif audio and not user_text:
    final_prompt = "User sent voice - reply: Walaikum Assalam! How can I help you? in 3 languages"

if final_prompt:
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        st.write(final_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                if image_to_send:
                    response = client.models.generate_content(
                        model="gemini-1.5-flash",
                        contents=[final_prompt, image_to_send]
                    )
                else:
                    response = client.models.generate_content(
                        model="gemini-1.5-flash",
                        contents=final_prompt
                    )
                answer = response.text

                # Google Translate Option
                if translate_on:
                    try:
                        trans = GoogleTranslator(source='auto', target=target_lang).translate(answer)
                        st.write(answer)
                        st.divider()
                        st.write(f"**🌐 Google Translated ({target_lang}):**")
                        st.write(trans)
                        answer = f"{answer}\n\nTranslated: {trans}"
                    except:
                        st.write(answer)
                else:
                    st.write(answer)

                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"Error: {e}")
