import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
# Streamlit cloud>settings>Secrets paste and save code given below
# GENAI_API_KEY = "your_gemini_api_key_here"

# ---- STREAMLIT SETUP ----
st.set_page_config(page_title="Gemini 2.0 Flash Chatbot", page_icon="🤖")
st.title("🤖 Gemini 2.0 Flash Chatbot with Uploads")

# ---- API KEY FROM SECRETS ----
api_key = st.secrets["GENAI_API_KEY"]
genai.configure(api_key=api_key)


# ---- GEMINI 2.0 FLASH MODEL ----
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

# ---- INITIALIZE CHAT ----
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat()

# ---- SIDEBAR FILE UPLOAD ----
st.sidebar.header("📎 Attach Files or Images")
uploaded_files = st.sidebar.file_uploader(
    "Upload text or images",
    type=["txt", "png", "jpg", "jpeg", "csv"],
    accept_multiple_files=True,
)

# Convert uploads to Gemini content parts
attachments = []
if uploaded_files:
    for file in uploaded_files:
        if file.type.startswith("image/"):
            img = Image.open(file)
            attachments.append({"mime_type": file.type, "data": file.read()})
            st.sidebar.image(img, caption=file.name)
        else:
            content = file.read().decode("utf-8", errors="ignore")
            attachments.append({"text": content})
            st.sidebar.success(f"Attached: {file.name}")

# ---- USER INPUT ----
user_input = st.chat_input("Ask something...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Thinking..."):
        if attachments:
            response = st.session_state.chat.send_message(
                [user_input] + attachments
            )
        else:
            response = st.session_state.chat.send_message(user_input)

    with st.chat_message("assistant"):
        st.markdown(response.text)

# ---- DISPLAY CHAT HISTORY ----
for msg in st.session_state.chat.history:
    with st.chat_message(msg.role):
        for part in msg.parts:
            if hasattr(part, "text"):
                st.markdown(part.text)
            elif hasattr(part, "inline_data") and hasattr(part.inline_data, "data"):
                st.image(io.BytesIO(part.inline_data.data), caption="Attached Image")
