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

# ---- SESSION STATE FOR CHAT ----
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat()

# ---- FILE UPLOADS ----
st.sidebar.header("📎 Upload Files (CSV, TXT, Images)")
uploaded_files = st.sidebar.file_uploader(
    "Upload files",
    type=["csv", "txt", "png", "jpg", "jpeg"],
    accept_multiple_files=True,
)

attachments = []

# ---- HANDLE FILES ----
if uploaded_files:
    for file in uploaded_files:
        mime = file.type or "application/octet-stream"

        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
            content = df.to_csv(index=False)
            blob = genai.upload_file(data=content.encode("utf-8"), mime_type="text/plain")
            attachments.append(blob)
            st.sidebar.success(f"Attached CSV: {file.name}")

        elif file.name.endswith(".txt"):
            text = file.read().decode("utf-8", errors="ignore")
            blob = genai.upload_file(data=text.encode("utf-8"), mime_type="text/plain")
            attachments.append(blob)
            st.sidebar.success(f"Attached TXT: {file.name}")

        elif mime.startswith("image/"):
            image_data = file.read()
            blob = genai.upload_file(data=image_data, mime_type=mime)
            attachments.append(blob)
            st.sidebar.image(Image.open(file), caption=file.name)

        else:
            st.sidebar.warning(f"Unsupported file type: {file.name}")

# ---- USER PROMPT ----
user_input = st.chat_input("Ask a question...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Thinking..."):
        response = st.session_state.chat.send_message(
            user_input,
            files=attachments if attachments else None
        )

    with st.chat_message("assistant"):
        st.markdown(response.text)

# ---- DISPLAY CHAT HISTORY ----
for msg in st.session_state.chat.history:
    if hasattr(msg, "role") and hasattr(msg, "parts"):
        with st.chat_message(msg.role):
            for part in msg.parts:
                if hasattr(part, "text"):
                    st.markdown(part.text)
