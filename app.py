import os
import streamlit as st
from dotenv import load_dotenv

from utils.pdf_helper import extract_text_from_pdf
from utils.ai_helper import (
    simplify_content,
    generate_summary,
    generate_mcqs,
    generate_exam_questions,
    explain_keywords,
    answer_question,
    auto_detect_level,
    generate_study_plan,
    find_difficult_concepts,
)

# ─────────────────────────────────────────────────────────────
# Setup
# ─────────────────────────────────────────────────────────────
load_dotenv()

st.set_page_config(
    page_title="EduEase AI",
    page_icon="📚",
    layout="wide",
)

# ─────────────────────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .main {
        background-color: #eef3ff;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    .hero-title {
        font-size: 2.7rem;
        font-weight: 800;
        color: #1d2b64;
        margin-bottom: 0.2rem;
    }

    .hero-subtitle {
        font-size: 1.1rem;
        color: #4b5b7c;
        margin-bottom: 1rem;
    }

    .info-banner {
        background: #e9f3ff;
        border: 1px solid #b6d8ff;
        padding: 14px 18px;
        border-radius: 12px;
        color: #1c3d6e;
        margin-bottom: 1rem;
        font-size: 1rem;
    }

    .section-title {
        font-size: 2rem;
        font-weight: 800;
        color: #32457a;
        margin: 1rem 0 0.7rem 0;
    }

    .output-box {
        background: #ffffff;
        border-left: 6px solid #4056c6;
        padding: 24px;
        border-radius: 14px;
        color: #111827;
        font-size: 1rem;
        line-height: 1.7;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
        white-space: pre-wrap;
    }

    .empty-state {
        background: #ffffff;
        border: 2px dashed #c8d3f5;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        color: #56627a;
    }

    .small-note {
        font-size: 0.9rem;
        color: #5b6680;
    }

    .footer-text {
        text-align: center;
        color: #6b7280;
        font-size: 0.95rem;
        margin-top: 2rem;
        padding-top: 1rem;
    }

    .sidebar-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: white;
        margin-bottom: 0.4rem;
    }

    .sidebar-sub {
        font-size: 1rem;
        color: #d9e2ff;
        line-height: 1.5;
    }

    .sidebar-box {
        background: rgba(255,255,255,0.08);
        padding: 14px;
        border-radius: 12px;
        color: white;
        margin-top: 1rem;
    }

    .stButton > button {
        width: 100%;
        border-radius: 12px;
        padding: 0.65rem 1rem;
        font-weight: 700;
        border: none;
    }

    .api-box {
        background: #18213d;
        color: #ffffff;
        padding: 12px 14px;
        border-radius: 10px;
        font-family: monospace;
        font-size: 0.95rem;
        line-height: 1.7;
        margin-top: 0.6rem;
    }

    .detected-level {
        background: #eef7ff;
        border: 1px solid #cfe5ff;
        color: #174a8b;
        padding: 10px 14px;
        border-radius: 10px;
        margin-top: 0.5rem;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-title">📚 EduEase AI</div>
        <div class="sidebar-sub">
            IBM watsonx-powered<br>
            Course Content Simplification Agent
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    st.markdown("## How to use")
    st.markdown(
        """
1. Upload a PDF **or** paste text  
2. Click **Extract Content**  
3. Choose learner level  
4. Use any AI action button  
5. Read the generated output
"""
    )

    st.markdown("---")

    st.markdown("## Learner Level")
    level = st.selectbox(
        "Select learner level",
        ["Beginner", "Intermediate", "Expert", "Auto Detect"],
    )

    st.markdown("---")

    st.markdown("## API Status")
    st.caption("Set your credentials in `.env`")

    api_key = os.getenv("WATSONX_API_KEY", "").strip()
    project_id = os.getenv("WATSONX_PROJECT_ID", "").strip()
    region = os.getenv("WATSONX_REGION", "us-south").strip()

    if api_key and project_id:
        st.success("IBM watsonx configured")
        st.markdown(
            f"""
            <div class="api-box">
            WATSONX_API_KEY = ✔ configured<br>
            WATSONX_PROJECT_ID = ✔ configured<br>
            WATSONX_REGION = {region}
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.warning("IBM watsonx credentials missing")
        st.markdown(
            """
            <div class="api-box">
            WATSONX_API_KEY = ...<br>
            WATSONX_PROJECT_ID = ...<br>
            WATSONX_REGION = us-south
            </div>
            """,
            unsafe_allow_html=True,
        )

# ─────────────────────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────────────────────
if "working_text" not in st.session_state:
    st.session_state.working_text = ""

if "detected_level" not in st.session_state:
    st.session_state.detected_level = ""

if "last_output" not in st.session_state:
    st.session_state.last_output = ""

if "last_title" not in st.session_state:
    st.session_state.last_title = ""

# ─────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">EduEase AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">Course Content Simplification Agent <span style="font-size:0.95rem;color:#4f63b5;">Powered by IBM watsonx.ai</span></div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="info-banner">
        🎓 Upload your study material or paste academic content below. Then use AI to simplify, summarise, generate quizzes, build a study plan, detect difficult concepts, and answer questions from the content.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# ─────────────────────────────────────────────────────────────
# Input section
# ─────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("## 📄 Upload PDF Notes")
    uploaded_file = st.file_uploader(
        "Drag & drop or browse a PDF file",
        type=["pdf"],
        label_visibility="collapsed"
    )

with col2:
    st.markdown("## ✏️ Or Paste Text Manually")
    manual_text = st.text_area(
        "Paste your academic notes here",
        height=220,
        placeholder="Paste lecture notes, textbook paragraphs, or any academic content...",
        label_visibility="collapsed"
    )

extract_btn = st.button("🔎 Extract Content", use_container_width=False)

if extract_btn:
    extracted_text = ""

    if uploaded_file is not None:
        try:
            extracted_text = extract_text_from_pdf(uploaded_file)
            if extracted_text.strip():
                st.session_state.working_text = extracted_text.strip()
                st.success("PDF content extracted successfully.")
            else:
                st.warning("No readable text found in the PDF. It may be a scanned/image PDF.")
        except Exception as e:
            st.error(f"Error reading PDF: {e}")

    elif manual_text.strip():
        st.session_state.working_text = manual_text.strip()
        st.success("Text loaded successfully.")

    else:
        st.warning("Please upload a PDF or paste some academic text first.")

# ─────────────────────────────────────────────────────────────
# Show extracted content preview
# ─────────────────────────────────────────────────────────────
if st.session_state.working_text:
    with st.expander("📘 View extracted / loaded content", expanded=False):
        preview = st.session_state.working_text[:4000]
        st.write(preview)
        if len(st.session_state.working_text) > 4000:
            st.caption("Preview truncated for display.")

st.markdown("---")

# ─────────────────────────────────────────────────────────────
# AI Action Buttons
# ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🤖 AI-Powered Actions</div>', unsafe_allow_html=True)
st.caption("Click any button below to generate the corresponding output from your content.")

btn_col1, btn_col2, btn_col3 = st.columns(3)

with btn_col1:
    simplify_btn = st.button("💡 Simplify Content")
    mcq_btn = st.button("❓ Generate MCQs")
    keyword_btn = st.button("🔑 Explain Keywords")

with btn_col2:
    summary_btn = st.button("📝 Generate Summary")
    exam_btn = st.button("📋 Exam Questions")
    study_btn = st.button("📚 Generate Study Plan")

with btn_col3:
    difficult_btn = st.button("⚠️ Find Difficult Concepts")
    detect_btn = st.button("🧠 Auto Detect Level")

st.markdown("### 💬 Ask a Question from the Content")
user_question = st.text_input(
    "Type a question based on the uploaded / pasted content",
    placeholder="Example: What is Python used for?"
)
ask_btn = st.button("Ask Question")

# ─────────────────────────────────────────────────────────────
# Helper: get actual learner level
# ─────────────────────────────────────────────────────────────
def get_actual_level():
    if level == "Auto Detect":
        detected = auto_detect_level(st.session_state.working_text)
        st.session_state.detected_level = detected
        return detected
    return level

# ─────────────────────────────────────────────────────────────
# Handle actions
# ─────────────────────────────────────────────────────────────
if st.session_state.working_text:
    working_text = st.session_state.working_text

    if simplify_btn:
        actual_level = get_actual_level()
        result = simplify_content(working_text, actual_level)
        st.session_state.last_title = "💡 Simplified Content"
        st.session_state.last_output = result

    elif summary_btn:
        actual_level = get_actual_level()
        result = generate_summary(working_text, actual_level)
        st.session_state.last_title = "📝 Summary"
        st.session_state.last_output = result

    elif mcq_btn:
        actual_level = get_actual_level()
        result = generate_mcqs(working_text, actual_level)
        st.session_state.last_title = "❓ Multiple Choice Questions"
        st.session_state.last_output = result

    elif exam_btn:
        actual_level = get_actual_level()
        result = generate_exam_questions(working_text, actual_level)
        st.session_state.last_title = "📋 Important Exam Questions"
        st.session_state.last_output = result

    elif keyword_btn:
        actual_level = get_actual_level()
        result = explain_keywords(working_text, actual_level)
        st.session_state.last_title = "🔑 Keywords & Explanations"
        st.session_state.last_output = result

    elif study_btn:
        actual_level = get_actual_level()
        result = generate_study_plan(working_text, actual_level)
        st.session_state.last_title = "📚 Personalized Study Plan"
        st.session_state.last_output = result

    elif difficult_btn:
        actual_level = get_actual_level()
        result = find_difficult_concepts(working_text, actual_level)
        st.session_state.last_title = "⚠️ Difficult Concepts"
        st.session_state.last_output = result

    elif detect_btn:
        detected = auto_detect_level(working_text)
        st.session_state.detected_level = detected
        st.session_state.last_title = "🧠 Auto Detected Learner Level"
        st.session_state.last_output = f"Recommended learner level for this content: **{detected}**"

    elif ask_btn:
        if user_question.strip():
            actual_level = get_actual_level()
            result = answer_question(working_text, user_question.strip(), actual_level)
            st.session_state.last_title = "💬 Answer to Your Question"
            st.session_state.last_output = result
        else:
            st.warning("Please type a question first.")

else:
    if any([simplify_btn, summary_btn, mcq_btn, exam_btn, keyword_btn, study_btn, difficult_btn, detect_btn, ask_btn]):
        st.warning("Please upload a PDF or paste academic text, then click Extract Content first.")

# ─────────────────────────────────────────────────────────────
# Show detected level if available
# ─────────────────────────────────────────────────────────────
if st.session_state.detected_level:
    st.markdown(
        f"""
        <div class="detected-level">
            🧠 Detected learner level: <b>{st.session_state.detected_level}</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────
# Output Section
# ─────────────────────────────────────────────────────────────
st.markdown("---")

if st.session_state.last_output:
    st.markdown(
        f'<div class="section-title">{st.session_state.last_title}</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div class="output-box">{st.session_state.last_output}</div>',
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <div class="empty-state">
            <div style="font-size:3rem;">📂</div>
            <h3 style="margin:0.4rem 0;color:#32457a;">No content loaded yet</h3>
            <p style="margin:0;font-size:1rem;">
                Upload a PDF or paste academic text above, then click
                <strong>Extract Content</strong> to begin.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div class="footer-text">EduEase AI · IBM Internship Project · Powered by IBM watsonx.ai</div>',
    unsafe_allow_html=True
)