# Import necessary libraries
import os
import google.generativeai as genai
import pandas as pd
from PyPDF2 import PdfReader
from docx import Document
import streamlit as st
import re

# Configure the API key
genai.configure(api_key="AIzaSyBZpbom7fJNrW_J_ZgbWvq_JGgtu0xTMZ0")

# Initialize the model
model = genai.GenerativeModel("gemini-1.5-flash")

# Function to read text from PDF
def read_pdf(file):
    pdf = PdfReader(file)
    text = ''
    for page in pdf.pages:
        text += page.extract_text()
    return text

# Function to read text from Word document
def read_docx(file):
    doc = Document(file)
    text = ''
    for para in doc.paragraphs:
        text += para.text
    return text

# Function to get resume text based on file extension
def get_resume_text(uploaded_file):
    if uploaded_file.type == 'application/pdf':
        return read_pdf(uploaded_file)
    elif uploaded_file.type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        return read_docx(uploaded_file)
    else:
        return ''

# Function to predict resume suitability using Gemini
def predict_suitability(resume_text, job_description):
    prompt = f"Job Description:\n{job_description}\n\nResume Text:\n{resume_text}\n\nIs this resume suitable for the job? Provide a suitability score from 0 to 100."
    response = model.generate_content(prompt)

    # Extract numerical suitability score from response text using regex
    match = re.search(r'\b\d+\b', response.text)
    if match:
        suitability_score = int(match.group())
    else:
        suitability_score = 0  # Default to 0 if no numerical score is found

    return suitability_score

# Streamlit app
def main():
    st.title('Resume Application Tracking System (ATS)')

    job_description = st.text_area("Enter the Job Description:")
    upload_files = st.file_uploader("Upload Resumes", type=['pdf', 'docx'], accept_multiple_files=True)

    if st.button('Process Resumes'):
        suitable_resumes = []
        unsuitable_resumes = []

        for upload_file in upload_files:
            resume_text = get_resume_text(upload_file)
            suitability_score = predict_suitability(resume_text, job_description)
            st.write(f"Resume: {upload_file.name}, Suitability Score: {suitability_score}")

            if suitability_score >= 50:
                suitable_resumes.append(upload_file)
            else:
                unsuitable_resumes.append(upload_file)

        st.write("Suitable Resumes:", [f.name for f in suitable_resumes])
        st.write("Unsuitable Resumes:", [f.name for f in unsuitable_resumes])

        # Create folders and move files accordingly
        if not os.path.exists('Suitable_Resumes'):
            os.makedirs('Suitable_Resumes')
        if not os.path.exists('Unsuitable_Resumes'):
            os.makedirs('Unsuitable_Resumes')

        for upload_file in suitable_resumes:
            with open(os.path.join('Suitable_Resumes', upload_file.name), "wb") as f:
                f.write(upload_file.getbuffer())

        for upload_file in unsuitable_resumes:
            with open(os.path.join('Unsuitable_Resumes', upload_file.name), "wb") as f:
                f.write(upload_file.getbuffer())

if __name__ == "__main__":
    main()
