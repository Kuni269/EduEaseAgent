# EduEase AI – Personalised Learning Agent

> **IBM Internship Project** | Powered by IBM watsonx.ai · **IBM Granite** (`ibm/granite-3-3-8b-instruct`)

EduEase AI is a Streamlit application that solves the core challenge of educational content accessibility.
It analyses academic material and **re-frames explanations based on the learner's proficiency level** —
from complete beginner to domain expert — supporting inclusive, personalised education at scale.

---

## 🎯 The Problem Solved

> *"Educational materials often vary in complexity and are not always accessible to learners with different
> levels of prior knowledge."*

EduEase AI addresses this by:

- **Detecting** the learner's current proficiency (Beginner / Intermediate / Expert)
- **Adapting** every AI-generated output — explanations, summaries, MCQs, exam questions, and keyword
  definitions — to that exact level
- **Empowering** students to ask free-form questions and receive answers calibrated to their understanding
- **Running entirely** on IBM Cloud Lite services with the mandatory IBM Granite model

---

## ✨ Features

| # | Feature | Where |
|---|---------|-------|
| 1 | Upload PDF notes (text-based) | File uploader |
| 2 | Paste academic text manually | Text area |
| 3 | Extract & preview content | 🔍 Extract Content |
| 4 | **Select proficiency level** | Sidebar selector |
| 5 | Explain content at learner's level | 💡 Explain at My Level |
| 6 | Generate a level-calibrated summary | 📝 Generate Summary |
| 7 | Create MCQs at the right difficulty | ❓ Generate MCQs |
| 8 | Set exam questions at the right depth | 📋 Exam Questions |
| 9 | Explain keywords at the right level | 🔑 Explain Keywords |
| 10 | **Ask a question – Q&A chat mode** | 💬 Ask a Question tab |

---

## 🗂️ Project Structure

```
EduEaseAgent/
│
├── app.py                  ← Main Streamlit application
├── requirements.txt        ← Python dependencies
├── .env.example            ← Template for your API credentials
├── .env                    ← Your real credentials (DO NOT commit)
│
└── utils/
    ├── __init__.py
    ├── ai_helper.py        ← All IBM watsonx.ai / Granite API calls
    └── pdf_helper.py       ← PDF text extraction (PyMuPDF)
```

---

## 🚀 Quick Start

### 1. Clone or download the project

```bash
git clone https://github.com/your-username/EduEaseAgent.git
cd EduEaseAgent
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your IBM credentials

```bash
# Windows
copy .env.example .env
# macOS / Linux
cp .env.example .env
```

Open `.env` and fill in your values:

```
WATSONX_API_KEY=your_ibm_cloud_api_key
WATSONX_PROJECT_ID=your_watsonx_project_id
WATSONX_REGION=us-south
```

### 5. Run the app

```bash
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`.

---

## 🔑 Getting IBM watsonx.ai Credentials (Free Lite Plan)

1. Sign up for a free IBM Cloud account: https://cloud.ibm.com/registration
2. Create a **watsonx.ai** instance (Lite plan is sufficient)
3. Go to **Manage → Access (IAM)** and create an **API key**
4. In watsonx.ai Studio, copy your **Project ID** from Project Settings → General
5. Paste both into your `.env` file

**Model used:** `ibm/granite-3-3-8b-instruct` — IBM Granite family, available on the free Lite plan.

---

## 🧠 How Proficiency Levels Work

Each AI action sends a carefully engineered prompt to IBM Granite that describes the target audience:

| Level | Prompt Instruction |
|-------|-------------------|
| **Beginner** | Everyday words, short sentences, real-world analogies, zero jargon |
| **Intermediate** | Standard academic vocabulary, brief term definitions, concept bridging |
| **Expert** | Precise technical language, full depth, advanced concept references |

The selected level applies to **all** actions: explanations, summaries, MCQs, exam questions, keywords,
and Q&A answers — so a student never needs to manually request simpler language.

---

## 🛠️ Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | Web UI framework |
| `PyMuPDF` | PDF text extraction |
| `requests` | HTTP calls to IBM watsonx.ai REST API |
| `python-dotenv` | Load `.env` credentials |

---

## 📌 Notes for Evaluators

- **IBM Granite** (`ibm/granite-3-3-8b-instruct`) is the mandatory model — enforced in `utils/ai_helper.py`
- **IBM watsonx.ai REST API** is used directly via `requests` — no external SDK dependency
- **Proficiency-level personalisation** is the core differentiator: every prompt is dynamically
  adapted based on the learner's declared level
- **Q&A chat tab** provides an agentic question-answering experience grounded in the uploaded content
- The app runs entirely on IBM Cloud Lite services, meeting the project requirement
- All API calls, prompt templates, and level logic are clearly documented in `utils/ai_helper.py`

---

## 📄 License

Built as part of an IBM Internship Programme. Free to use and modify for educational purposes.
