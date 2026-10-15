import streamlit as st
from google import genai
from PIL import Image

st.set_page_config(page_title="Meta AI Pro FAST", page_icon="⚡", layout="wide")
st.markdown('<h2 style="text-align:center;">⚡ Meta AI Pro - FAST</h2>', unsafe_allow_html=True)

client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
MODEL = "gemini-3.5-flash-lite" # NEW 2026 FASTEST - 350 tokens/sec!

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

uploaded = st.file_uploader("📷 Photo", type=["jpg","jpeg","png","webp"])
image_for_chat = None
if uploaded:
    img = Image.open(uploaded)
    img.thumbnail((512, 512)) # Make fast
    image_for_chat = img
    st.image(img, width=200)

prompt = st.chat_input("Ask...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_text = ""
        try:
            # NEW FAST STREAMING
            for chunk in client.models.generate_content_stream(
                model=MODEL,
                contents=[prompt, image_for_chat] if image_for_chat else prompt
            ):
                if chunk.text:
                    full_text += chunk.text
                    placeholder.markdown(full_text + "▌")
            placeholder.markdown(full_text)
            st.session_state.messages.append({"role": "assistant", "content": full_text})
        except Exception as e:
            st.error(f"Error: {e}")
            st.info("Trying backup model...")
            try:
                resp = client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
                st.write(resp.text)
            except Exception as e2:
                st.error(f"Backup also busy: {e2}")
