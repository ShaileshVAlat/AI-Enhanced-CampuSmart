import os
from datetime import datetime
from PyPDF2 import PdfReader
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import base64

# Optional self-bootstrap for standalone port setting
if "STREAMLIT_SERVER_PORT" not in os.environ:
    os.environ["STREAMLIT_SERVER_PORT"] = "2222"
    os.environ["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"
    import streamlit.web.cli as stcli
    import sys
    sys.argv = ["streamlit", "run", sys.argv[0]]
    sys.exit(stcli.main())

# Page configuration
st.set_page_config(
    page_title="T&P Cell Chatbot",
    page_icon="🎓",
    layout="wide"
)

# Load API key & configure Gemini
dotenv_path = os.path.join(os.getcwd(), '.env')
load_dotenv(dotenv_path)
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

# Pre-load the T&P PDF from disk
PDF_PATH = "tnp.pdf"
if not os.path.exists(PDF_PATH):
    st.error(f"Could not find {PDF_PATH} in the working directory.")
    st.stop()

@st.cache_data
def load_pdf_text(path):
    reader = PdfReader(path)
    return "".join(p.extract_text() or "" for p in reader.pages)

pdf_text = load_pdf_text(PDF_PATH)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# ============ Function for Base64 Background ============ #
def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Load background image
bg_image = get_base64_of_bin_file("instance-bg.jpg")

# ============ CSS for Styling ============ #
st.markdown(f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("data:image/png;base64,{bg_image}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}}
.block-container {{
    background: rgba(255, 255, 255, 0.85);
    padding: 2rem !important;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}}

/* Chat container */
.chat-container {{
    max-height: 500px;
    overflow-y: auto;
    padding: 10px;
    border: 1px solid #8e24aa;
    background: #f3e6fa;
    color: #000 !important;
    border-radius: 12px;
}}

/* Chat bubbles */
.chat-bubble {{
    padding: 10px 15px;
    border-radius: 12px;
    margin: 5px;
    display: inline-block;
    max-width: 75%;
    box-shadow: 0 1px 3px rgba(142,36,170,0.08);
    line-height: 1.4;
    color: #000 !important;
}}
.user {{
    background-color: #8e24aa !important;
    color: #fff !important;
    float: right;
    text-align: right;
}}
.bot {{
    background-color: #e1bee7 !important;
    color: #000 !important;
    float: left;
    text-align: left;
}}
.clear {{ clear: both; }}
.timestamp {{
    font-size: 0.8em;
    color: #8e24aa !important;
    margin-top: 5px;
    display: block;
}}
</style>
""", unsafe_allow_html=True)

# ============ Header with Logo + Permanent Color ============ #
col1, col2 = st.columns([1, 8])
with col1:
    st.image("logo (1).png", width='stretch') # College logo
with col2:
    st.markdown(
        "<h1 style='color:white; background-color:#6a1b9a; padding:15px; border-radius:10px;'>🎓 Training & Placement Cell Chatbot</h1>",
        unsafe_allow_html=True
    )

st.markdown(
    "<p style='color:black; font-size:18px;'>Ask any question about our T&P processes, deadlines, or contacts.</p>",
    unsafe_allow_html=True
)

# Display chat history
chat_html = "<div class='chat-container'>"
for msg in st.session_state.messages:
    time_str = msg["time"]
    content = msg["content"]
    if msg["role"] == "user":
        chat_html += (
            f"<div class='chat-bubble user'>👤 {content}"
            f"<div class='timestamp'>{time_str}</div></div><div class='clear'></div>"
        )
    else:
        chat_html += (
            f"<div class='chat-bubble bot'>🤖 {content}"
            f"<div class='timestamp'>{time_str}</div></div><div class='clear'></div>"
        )
chat_html += "</div>"
st.markdown(chat_html, unsafe_allow_html=True)

# User input via chat_input
user_input = st.chat_input("Type your question here...")
if user_input:
    now = datetime.now().strftime("%I:%M %p")
    st.session_state.messages.append({"role": "user", "content": user_input, "time": now})

    # Construct strict prompt
    prompt = f"""
You are an expert assistant for our college’s Training & Placement (T&P) Cell.
Answer using ONLY the information in this PDF and details of company if not present in pdf by yourself like interview proccess and questions expected:

PDF CONTENT START
{pdf_text}
PDF CONTENT END

Student question: {user_input}

If the PDF doesn’t cover it, reply “I’m sorry, I don’t have that information.”
Keep answers concise (1–3 sentences), use bullet points if needed.
Also don't mention it is from PDF. But if student asks for any company detail or what interview question can be expected, answer that.
"""
    with st.spinner("Thinking..."):
        response = model.generate_content(prompt)
        bot_reply = response.text.strip()

    now_bot = datetime.now().strftime("%I:%M %p")
    st.session_state.messages.append({"role": "assistant", "content": bot_reply, "time": now_bot})
    st.rerun()