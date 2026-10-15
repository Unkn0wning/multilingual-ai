import streamlit as st
from google import genai
from PIL import Image
import time

st.set_page_config(page_title="Meta AI Pro", page_icon="🤖", layout="wide")
st.markdown('<h2 style="text-align:center;">🤖 Meta AI Pro</h2>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:gray;">Ask anything • Upload Photo/Video • Edit Images • Translate</p>', unsafe_allow_html=True)

client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

# AUTO-FALLBACK MODELS - If one is busy, tries next
MODELS_TO_TRY = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-3.5-flash", "gemini-2.0-flash-lite"]

with st.sidebar:
    st.title("⚙️ Settings")
    lang = st.selectbox("Reply Language", ["Auto", "Urdu", "Pashto", "English"])
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("image"):
            st.image(msg["image"], width=200)
        st.write(msg["content"])

uploaded = st.file_uploader("📷 Photo / Video for edit", type=["jpg","jpeg","png","mp4","mov","webp"])
image_for_chat = None
if uploaded:
    if uploaded.type.startswith("image"):
        image_for_chat = Image.open(uploaded)
        st.image(image_for_chat, width=200)
    else:
        st.video(uploaded)

prompt = st.chat_input("Ask... or upload photo and say 'make cartoon, remove background, make HD'")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt, "image": image_for_chat})
    with st.chat_message("user"):
        if image_for_chat:
            st.image(image_for_chat, width=200)
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Meta AI is thinking..."):
            answer = None
            last_error = ""
            # Try all models one by one
            for MODEL in MODELS_TO_TRY:
                try:
                    sys = f"You are Meta AI Pro. Lang: {lang}. User: {prompt}"
                    if image_for_chat:
                        resp = client.models.generate_content(model=MODEL, contents=[sys, image_for_chat])
                    else:
                        resp = client.models.generate_content(model=MODEL, contents=sys)
                    answer = resp.text
                    st.success(f"Using model: {MODEL}")
                    break
                except Exception as e:
                    last_error = str(e)
                    if "503" in last_error or "UNAVAILABLE" in last_error:
                        continue # Try next model
                    else:
                        time.sleep(1)
                        continue
            
            if answer:
                st.write(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.error(f"All models busy right now. Please wait 1 min and try again. Last error: {last_error}")
