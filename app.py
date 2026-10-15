import streamlit as st
from google import genai
from PIL import Image

st.set_page_config(page_title="Meta AI Pro Fast", page_icon="⚡", layout="wide")
st.markdown('<h2 style="text-align:center;">⚡ Meta AI Pro - FAST</h2>', unsafe_allow_html=True)

client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
MODEL = "gemini-2.0-flash-lite"  # FASTEST MODEL - 2x faster than 3.5!

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# COMPRESS IMAGE TO MAKE FAST
uploaded = st.file_uploader("📷 Photo", type=["jpg","jpeg","png","webp"])
image_for_chat = None
if uploaded:
    img = Image.open(uploaded)
    # Resize to 512px to make 10x faster!
    img.thumbnail((512, 512))
    image_for_chat = img
    st.image(image_for_chat, width=200, caption="Compressed for speed ⚡")

prompt = st.chat_input("Ask...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        # STREAMING = FAST, shows words as it thinks!
        placeholder = st.empty()
        full_text = ""
        try:
            # Use streaming for instant speed
            response = client.models.generate_content_stream(
                model=MODEL,
                contents=prompt if not image_for_chat else [prompt, image_for_chat]
            )
            for chunk in response:
                if chunk.text:
                    full_text += chunk.text
                    placeholder.write(full_text + "▌")
            placeholder.write(full_text)
            st.session_state.messages.append({"role": "assistant", "content": full_text})
        except Exception as e:
            # Fallback if stream fails
            try:
                resp = client.models.generate_content(model=MODEL, contents=prompt)
                st.write(resp.text)
                st.session_state.messages.append({"role": "assistant", "content": resp.text})
            except Exception as e2:
                st.error(f"Error: {e2}")
