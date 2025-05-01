import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
# Streamlit cloud>settings>Secrets paste and save code given below
# GENAI_API_KEY = "your_gemini_api_key_here"

api_key = st.secrets["GENAI_API_KEY"]
genai.configure(api_key=api_key)

# ---- SETUP ----
st.set_page_config(page_title="Gemini Flash 2 Chatbot", page_icon="🤖")

st.title("🤖 Gemini Flash 2 Chatbot with Uploads")

# Set your API key here (or use st.secrets for safety)
#genai.configure(api_key="YOUR_API_KEY")

# Load Gemini Flash 2 model
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

# Initialize session state
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

# ---- FILE UPLOAD ----
st.sidebar.header("📎 Attach Files")
uploaded_files = st.sidebar.file_uploader(
    "Upload file(s), screenshot or image",
    accept_multiple_files=True,
    type=["txt", "pdf", "png", "jpg", "jpeg", "csv"],
)

attachments = []
if uploaded_files:
    for file in uploaded_files:
        if file.type.startswith("image/"):
            image = Image.open(file)
            attachments.append(genai.types.content.ImagePart.from_pil(image))
            st.sidebar.image(image, caption=file.name, use_column_width=True)
        else:
            content = file.read().decode("utf-8", errors="ignore")
            attachments.append(genai.types.content.TextPart(text=content))
            st.sidebar.success(f"Attached: {file.name}")

# ---- CHAT INTERFACE ----
user_input = st.chat_input("Ask anything...")

if user_input:
    st.session_state.chat.history.append({"role": "user", "parts": [user_input]})
    with st.spinner("Thinking..."):
        if attachments:
            response = st.session_state.chat.send_message([user_input] + attachments)
        else:
            response = st.session_state.chat.send_message(user_input)
    st.session_state.chat.history.append({"role": "model", "parts": [response.text]})

# Display chat history
for msg in st.session_state.chat.history:
    with st.chat_message(msg.role):
        for part in msg.parts:
            if hasattr(part, "text"):
                st.markdown(part.text)
            else:
                st.write(part)
