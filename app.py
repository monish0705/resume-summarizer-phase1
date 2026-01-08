import streamlit as st
import pdfplumber
import openai
import os


# Get OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Check if API key is set
if not openai.api_key:
    st.error(" OpenAI API key not found! Please set the OPENAI_API_KEY environment variable.")
    st.stop()

# EXTRACT TEXT FROM PDF


def extract_text_from_pdf(pdf_file):
    """
    Extracts text from all pages of a PDF file.
   """ 
   
    try:
        text = ""
        # Open PDF using pdfplumber
        with pdfplumber.open(pdf_file) as pdf:
            # Loop through each page
            for page in pdf.pages:
                # Extract text from current page
                page_text = page.extract_text()
                if page_text:  # Only add if text exists
                    text += page_text + "\n"
        
        # Clean up extra whitespace
        text = " ".join(text.split())
        return text
    
    except Exception as e:
        return f"Error extracting text: {str(e)}"


# FUNCTION 2: GENERATE SUMMARY USING LLM


def generate_summary(resume_text):
    """
    Generates a technical summary from resume text using OpenAI.
    """
    
    # Define the prompt with your requirements
    prompt = f"""You are a technical resume analyst specializing in tech industry roles.

Your task is to generate a detailed professional summary from the resume below.

Requirements:
- Focus on technical skills, tools, technologies, and engineering experience
- Use a direct, technical tone (avoid soft skills like "team player")
- Generate a detailed summary (not just 2-3 lines)
- Format the output as bullet points (3-5 bullets)
- DO NOT include personal information like phone numbers, email addresses, or home addresses
- Focus on: years of experience, key technologies, notable projects, technical expertise

Resume Text:
{resume_text}

Output Format:
- Bullet point 1
- Bullet point 2
- Bullet point 3
(etc.)
"""
    
    try:
        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Using GPT-4o-mini for cost-effectiveness
            messages=[
                {"role": "system", "content": "You are a technical resume analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,  # Controls randomness (0 = focused, 1 = creative)
            max_tokens=500    # Maximum length of response
        )
        
        # Extract the generated text
        summary = response.choices[0].message.content
        return summary
    
    except Exception as e:
        return f"Error generating summary: {str(e)}"


# STREAMLIT UI

# Set page configuration
st.set_page_config(
    page_title="Tech Resume Summarizer",
    page_icon="📄",
    layout="centered"
)

# Title and description
st.title("📄 Tech Resume Summarizer")
st.markdown("""
Upload a **tech resume (PDF)** and get an instant detailed technical summary.

**Features:**
- Extracts text from PDF
- Generates detailed bullet-point summary
- Focuses on technical skills and experience
- Removes personal information
""")

st.divider()

# File uploader
uploaded_file = st.file_uploader(
    "Upload Resume (PDF only)", 
    type=["pdf"],
    help="Upload a tech resume in PDF format"
)

# Process when file is uploaded
if uploaded_file is not None:
    
    # Show file details
    st.success(f"✅ File uploaded: {uploaded_file.name}")
    
    # Add a "Generate Summary" button
    if st.button("🚀 Generate Summary", type="primary"):
        
        # Show spinner while processing
        with st.spinner("Extracting text from PDF..."):
            # Step 1: Extract text
            resume_text = extract_text_from_pdf(uploaded_file)
        
        # Check if extraction was successful
        if resume_text.startswith("Error"):
            st.error(resume_text)
        else:
            # Show extracted text in expander (for debugging)
            with st.expander("📝 View Extracted Text (Debug)"):
                st.text_area("Raw Text", resume_text, height=200)
            
            # Step 2: Generate summary
            with st.spinner("Generating technical summary..."):
                summary = generate_summary(resume_text)
            
            # Display the summary
            if summary.startswith("Error"):
                st.error(summary)
            else:
                st.subheader(" Technical Summary")
                st.markdown(summary)
                
                # Add download button for summary
                st.download_button(
                    label="📥 Download Summary",
                    data=summary,
                    file_name="resume_summary.txt",
                    mime="text/plain"
                )

# Footer
st.divider()
st.caption("Built with Streamlit + OpenAI | Phase 1: Basic Resume Summarizer")
