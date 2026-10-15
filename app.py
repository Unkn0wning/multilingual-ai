import streamlit as st
from google import genai

# Initialize the Gemini Client - CORRECT WAY FOR STREAMLIT
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

# System Instruction
system_instruction = "You are a helpful multilingual assistant fluent in English, Urdu, and Pashto."

st.title("🤖 My Multilingual AI (English, Urdu, Pashto)")
# System Instruction
system_instruction = "You are a helpful multilingual assistant fluent in English, Urdu, and Pashto."

st.title("🤖 My Multilingual AI (English, Urdu, Pashto)")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if user_input := st.chat_input("Type in English, Urdu (اردو), or Pashto (پښتو)..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=user_input,
            config={"system_instruction": system_instruction}
        )
        ai_reply = response.text
    except Exception as e:
        ai_reply = f"Error: {e}"

    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
    with st.chat_message("assistant"):
        st.markdown(ai_reply)
