import streamlit as st
from google import genai
from PIL import Image
from deep_translator import GoogleTranslator
import time

st.set_page_config(page_title="Meta AI Pro Clone", page_icon="🤖", layout="wide")

# --- PRO CSS ---
st.markdown("""
<style>
    .stChatMessage { border-radius: 20px; }
    header {visibility: hidden;}
    .big-title { font-size: 35px; font-weight: 800; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-title">🤖 Meta AI Pro</p>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:gray;">Ask anything • Upload Photo/Video • Edit Images • Translate</p>', unsafe_allow_html=True)

# --- CLIENT ---
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
MODEL = "gemini-3.5-flash"  # you said 3.5 works, keep your working one here - if fails change to your working name

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Settings")
    lang = st.selectbox("Reply Language", ["Auto (Urdu/Pashto/English)", "Urdu", "Pashto", "English"], index=0)
    translate = st.checkbox("Auto Translate", value=False)
    target = st.selectbox("Translate to", ["ur","ps","en"], index=0)
    st.divider()
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    st.caption("Built like Gemini • Voice + Vision + Edit")

# --- SESSION ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SHOW HISTORY ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("image"):
            st.image(msg["image"], width=250)
        st.write(msg["content"])

# --- INPUTS ---
col1, col2 = st.columns([4,1])
with col1:
    uploaded = st.file_uploader("📷 Photo / Video for edit", type=["jpg","jpeg","png","mp4","mov","webp"], label_visibility="collapsed")
with col2:
    audio = st.audio_input("🎤")

image_for_chat = None
if uploaded:
    if uploaded.type.startswith("image"):
        image_for_chat = Image.open(uploaded)
        st.image(image_for_chat, width=200, caption="Ready to edit")
    else:
        st.video(uploaded)

prompt = st.chat_input("Ask... or upload photo and say 'make cartoon, remove background, make HD'")

if prompt or (uploaded and not prompt):
    if not prompt:
        prompt = "Explain this photo/video in detail in Urdu, Pashto and English"
    
    # User bubble
    st.session_state.messages.append({"role": "user", "content": prompt, "image": image_for_chat})
    with st.chat_message("user"):
        if image_for_chat:
            st.image(image_for_chat, width=200)
        st.write(prompt)

    # AI bubble
    with st.chat_message("assistant"):
        with st.spinner("Meta AI is thinking..."):
            try:
                # PRO PROMPT FOR EDITING
                system_instruction = f"""
                You are Meta AI Pro. Professional, helpful, like Gemini.
                User language preference: {lang}
                If user uploaded image and asks to edit (cartoon, background, HD, etc):
                - Describe exactly how edited image would look (since you can't directly edit, give detailed prompt for editing)
                - Give step-by-step instructions to edit
                - If possible, describe final result vividly
                Always reply in 3 languages if user said salam or is Pashto/Urdu.
                Be concise, professional, with emojis.
                """

                full_prompt = system_instruction + "\n\nUser request: " + prompt

                if image_for_chat:
                    response = client.models.generate_content(
                        model=MODEL,
                        contents=[full_prompt, image_for_chat]
                    )
                else:
                    response = client.models.generate_content(
                        model=MODEL,
                        contents=full_prompt
                    )
                
                answer = response.text

                if translate:
                    try:
                        answer_trans = GoogleTranslator(source='auto', target=target).translate(answer)
                        st.write(answer)
                        st.divider()
                        st.caption(f"🌐 Translated to {target}:")
                        st.write(answer_trans)
                    except:
                        st.write(answer)
                else:
                    st.write(answer)
                
                st.session_state.messages.append({"role": "assistant", "content": answer})

            except Exception as e:
                st.error(f"Error: {e}. Try changing MODEL name to gemini-3.5-flash or your working one.")

# Footer
st.divider()
st.caption("💡 Try: Upload selfie + type 'make it professional LinkedIn photo' or 'make cartoon' or 'remove background'")
