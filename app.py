import os
import PyPDF2 as pdf
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# —————————————————————————————
#  Streamlit page config
st.set_page_config(
    page_title="Smart Application Tracking System",
    page_icon=":robot:",
    layout="wide"
)

# —————————————————————————————
# 1️⃣ Configure Google GenAI
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# 3️⃣ Pick a supported model
model = genai.GenerativeModel("gemini-2.5-flash")

# —————————————————————————————
# 🎨 App UI
st.title("SMART APPLICATION TRACKING SYSTEM")
st.text("Improve Your Resume ATS Score")

# Input fields
jd = st.text_area("Paste the Job Description")
uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type="pdf")

# Submission button
if st.button("Submit"):
    if uploaded_file is None:
        st.warning("Please upload a PDF resume.")
    elif not jd.strip():
        st.warning("Please enter the job description.")
    else:
        try:
            # 4️⃣ Extract text from PDF
            reader = pdf.PdfReader(uploaded_file)
            extracted_text = "".join(p.extract_text() or "" for p in reader.pages)

            # 5️⃣ Generate ATS feedback prompt
            prompt = f"""
You are a skilled ATS with deep understanding of software engineering, data science, and big data roles.
Evaluate the resume against the job description competitively. Return ONLY these sections:
• Job Description Match:
• Missing Keywords:
• Profile Summary:

Resume: {extracted_text}
Description: {jd}
"""
            # Call Google GenAI
            response = model.generate_content(prompt)

            # Show result
            st.markdown(response.text)

        except Exception as e:
            st.error(f"An error occurred: {e}")