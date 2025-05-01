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

# ---- CHAT INIT ----
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat()

# ---- UPLOADS ----
st.sidebar.header("📎 Upload Files (Images, CSV, Text)")
uploaded_files = st.sidebar.file_uploader(
    "Upload .png, .jpg, .txt, or .csv",
    type=["png", "jpg", "jpeg", "txt", "csv"],
    accept_multiple_files=True,
)

attachments = []
if uploaded_files:
    for file in uploaded_files:
        mime_type = file.type or "application/octet-stream"

        # Convert CSV to text
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
            content = df.to_csv(index=False)
            attachments.append({"mime_type": "text/plain", "data": content.encode("utf-8")})
            st.sidebar.success(f"Attached CSV: {file.name}")
        else:
            # Read bytes directly
            attachments.append({"mime_type": mime_type, "data": file.read()})
            if mime_type.startswith("image/"):
                st.sidebar.image(Image.open(file), caption=file.name)
            else:
                st.sidebar.success(f"Attached: {file.name}")

# ---- PROMPT ----
user_input = st.chat_input("Ask something...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Gemini is thinking..."):
        # Upload all attachments first
        uploaded_blobs = []
        for a in attachments:
            blob = genai.upload_file(data=a["data"], mime_type=a["mime_type"])
            uploaded_blobs.append(blob)

        # Send prompt with files
        response = st.session_state.chat.send_message(
            user_input,
            files=uploaded_blobs if uploaded_blobs else None
        )

    with st.chat_message("assistant"):
        st.markdown(response.text)
        # ---- DISPLAY CHAT HISTORY ----
for msg in st.session_state.chat.history:
    if hasattr(msg, "role") and hasattr(msg, "parts"):  # ensure it's a Gemini Content object
        with st.chat_message(msg.role):
            for part in msg.parts:
                if hasattr(part, "text"):
                    st.markdown(part.text)
