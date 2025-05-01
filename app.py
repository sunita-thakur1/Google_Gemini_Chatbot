import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
# Streamlit cloud>settings>Secrets paste and save code given below
# GENAI_API_KEY = "your_gemini_api_key_here"

# ---- CONFIG ----
st.set_page_config(page_title="Gemini Flash 2 Chatbot", page_icon="🤖")
st.title("🤖 Gemini Flash 2 Chatbot with File/Image Uploads")

# Configure Gemini
api_key = st.secrets["GENAI_API_KEY"]
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.0-flash")

# Chat initialization
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat()

# ---- FILE UPLOADS ----
st.sidebar.header("📎 Attach Files or Images")
uploaded_files = st.sidebar.file_uploader(
    "Upload text, screenshots, or image files",
    accept_multiple_files=True,
    type=["txt", "pdf", "png", "jpg", "jpeg", "csv"],
)

attachments = []
if uploaded_files:
    for file in uploaded_files:
        if file.type.startswith("image/"):
            img = Image.open(file)
            attachments.append(genai.types.content.ImagePart.from_pil(img))
            st.sidebar.image(img, caption=file.name)
        else:
            try:
                text = file.read().decode("utf-8", errors="ignore")
                attachments.append(genai.types.content.TextPart(text=text))
                st.sidebar.success(f"Text attached: {file.name}")
            except Exception as e:
                st.sidebar.error(f"Couldn't read {file.name}: {e}")

# ---- CHAT INPUT ----
prompt = st.chat_input("Ask something...")
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Gemini is thinking..."):
        response = (
            st.session_state.chat.send_message([prompt] + attachments)
            if attachments else
            st.session_state.chat.send_message(prompt)
        )

    with st.chat_message("assistant"):
        st.markdown(response.text)

# ---- DISPLAY HISTORY ----
for msg in st.session_state.chat.history:
    with st.chat_message(msg.role):
        for part in msg.parts:
            if hasattr(part, "text"):
                st.markdown(part.text)
