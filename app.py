import streamlit as st
import google.generativeai as genai

# Replace with your API key (Google AI studio API key)
# Link for Google AI studio to generate API key: https://aistudio.google.com/app/prompts/new_chat

# --- Set your Gemini API key ---
GENAI_API_KEY = "AIzaSyCHcN21zyLQNwsraNsv1I0rXiWDNduFvFY"
genai.configure(api_key=GENAI_API_KEY)

# --- Initialize Gemini Flash 2 model 
model = genai.GenerativeModel("gemini-2.0-flash")

# --- Session State for Chat History ---
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Streamlit App UI ---
st.title("💬 Gemini Flash 2 Chatbot")
st.markdown("Type your message below and interact with Google's Gemini model in real time.")

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
user_input = st.chat_input("Say something...")
if user_input:
    # Display user message
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Get response from Gemini Flash 2
    response = st.session_state.chat.send_message(user_input)
    reply = response.text

    # Display bot message
    st.chat_message("assistant").markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
