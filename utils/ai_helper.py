"""
ai_helper.py
─────────────────────────────────────────────
IBM watsonx.ai helper – all API calls go through here.

Model: ibm/granite-3-3-8b-instruct
Auth:  IAM API key → short-lived Bearer token
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

WATSONX_API_KEY = os.getenv("WATSONX_API_KEY", "").strip()
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID", "").strip()
WATSONX_REGION = os.getenv("WATSONX_REGION", "us-south").strip()

IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"
WATSONX_URL = f"https://{WATSONX_REGION}.ml.cloud.ibm.com"

# IBM Granite model
MODEL_ID = "ibm/granite-3-3-8b-instruct"

# Learner level context
_LEVEL_CONTEXT = {
    "Beginner": (
        "a complete beginner with no prior knowledge of the subject. "
        "Use very simple words, short sentences, relatable examples, and avoid technical jargon."
    ),
    "Intermediate": (
        "a student who has basic familiarity with the subject. "
        "Use moderate technical vocabulary, explain specialised terms briefly, and connect ideas clearly."
    ),
    "Expert": (
        "an advanced learner or domain expert. "
        "Use precise technical language, deeper explanation, and advanced detail where relevant."
    ),
}


# ─────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────

def _get_iam_token() -> str:
    """Exchange IBM Cloud API key for a short-lived IAM Bearer token."""
    response = requests.post(
        IAM_TOKEN_URL,
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": WATSONX_API_KEY,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=20,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"IAM token request failed ({response.status_code}): {response.text}"
        )

    return response.json()["access_token"]


def _generate(prompt: str, max_tokens: int = 600) -> str:
    """
    Send prompt to IBM watsonx.ai and return generated text.
    """
    if not WATSONX_API_KEY or not WATSONX_PROJECT_ID:
        return (
            "⚠️ Configuration missing — please add WATSONX_API_KEY and "
            "WATSONX_PROJECT_ID in your .env file."
        )

    try:
        token = _get_iam_token()

        url = f"{WATSONX_URL}/ml/v1/text/generation?version=2024-05-31"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        body = {
            "model_id": MODEL_ID,
            "input": prompt,
            "project_id": WATSONX_PROJECT_ID,
            "parameters": {
                "decoding_method": "greedy",
                "max_new_tokens": max_tokens,
                "min_new_tokens": 20,
                "repetition_penalty": 1.05,
            },
        }

        response = requests.post(url, headers=headers, json=body, timeout=90)

        if response.status_code != 200:
            return f"⚠️ IBM watsonx error ({response.status_code})\n\n{response.text}"

        result = response.json()

        if "results" in result and result["results"]:
            return result["results"][0].get("generated_text", "").strip()

        return "⚠️ IBM watsonx returned an empty result."

    except Exception as exc:
        return f"⚠️ IBM watsonx error: {exc}"


# ─────────────────────────────────────────────────────────────
# Agent upgrade feature 1: Auto detect learner level
# ─────────────────────────────────────────────────────────────

def auto_detect_level(text: str) -> str:
    """
    Detect whether the content is best suited for Beginner, Intermediate, or Expert explanation.
    Returns only one word: Beginner / Intermediate / Expert
    """
    prompt = (
        "You are an educational AI classifier.\n"
        "Read the following academic content and decide what learner level is most appropriate.\n\n"
        "Choose ONLY one from these options:\n"
        "- Beginner\n"
        "- Intermediate\n"
        "- Expert\n\n"
        "Return only the level name and nothing else.\n\n"
        f"Content:\n{text}\n\n"
        "Level:"
    )

    result = _generate(prompt, 20).strip()

    if "Expert" in result:
        return "Expert"
    elif "Intermediate" in result:
        return "Intermediate"
    else:
        return "Beginner"


# ─────────────────────────────────────────────────────────────
# Existing public features
# ─────────────────────────────────────────────────────────────

def simplify_content(text: str, level: str = "Beginner") -> str:
    ctx = _LEVEL_CONTEXT.get(level, _LEVEL_CONTEXT["Beginner"])
    prompt = (
        f"You are an expert teacher adapting academic material for {ctx}\n\n"
        "Rewrite the following academic content so it is perfectly suited to that audience. "
        "Keep all key ideas but adjust vocabulary, depth, and style to match the level.\n\n"
        f"Academic Content:\n{text}\n\n"
        "Rewritten Explanation:"
    )
    return _generate(prompt, 700)


def generate_summary(text: str, level: str = "Beginner") -> str:
    ctx = _LEVEL_CONTEXT.get(level, _LEVEL_CONTEXT["Beginner"])
    prompt = (
        f"You are summarising academic content for {ctx}\n\n"
        "Summarise the following content in clear bullet points. "
        "Adjust the depth and terminology to suit the audience level.\n\n"
        f"Content:\n{text}\n\n"
        "Summary (bullet points):"
    )
    return _generate(prompt, 500)


def generate_mcqs(text: str, level: str = "Beginner") -> str:
    ctx = _LEVEL_CONTEXT.get(level, _LEVEL_CONTEXT["Beginner"])
    prompt = (
        f"You are creating a quiz for {ctx}\n\n"
        "Generate exactly 5 multiple-choice questions from the following academic content.\n"
        "Rules:\n"
        "1. Each question must be based only on the given content.\n"
        "2. Each question must have 4 options: A, B, C, D.\n"
        "3. Mention the correct answer after each question.\n"
        "4. Make the difficulty match the learner level.\n\n"
        f"Content:\n{text}\n\n"
        "MCQs:"
    )
    return _generate(prompt, 750)


def generate_exam_questions(text: str, level: str = "Beginner") -> str:
    ctx = _LEVEL_CONTEXT.get(level, _LEVEL_CONTEXT["Beginner"])
    prompt = (
        f"You are setting exam questions for {ctx}\n\n"
        "Generate 5 important exam questions from the following academic content. "
        "Include a mix of short-answer and descriptive questions. "
        "Calibrate complexity and expected answer depth to match the audience level.\n\n"
        f"Content:\n{text}\n\n"
        "Exam Questions:"
    )
    return _generate(prompt, 600)


def explain_keywords(text: str, level: str = "Beginner") -> str:
    ctx = _LEVEL_CONTEXT.get(level, _LEVEL_CONTEXT["Beginner"])
    prompt = (
        f"You are explaining technical vocabulary to {ctx}\n\n"
        "Identify 5 to 7 important keywords from the following academic content. "
        "For each keyword, provide a concise explanation written at the right level for the audience.\n"
        "Format exactly like this:\n"
        "Keyword - explanation\n\n"
        f"Content:\n{text}\n\n"
        "Keywords and Explanations:"
    )
    return _generate(prompt, 500)


def answer_question(text: str, question: str, level: str = "Beginner") -> str:
    ctx = _LEVEL_CONTEXT.get(level, _LEVEL_CONTEXT["Beginner"])
    prompt = (
        f"You are a knowledgeable tutor answering a question for {ctx}\n\n"
        "Use only the provided academic content as your source. "
        "If the answer is not clearly in the content, say so honestly.\n\n"
        f"Academic Content:\n{text}\n\n"
        f"Student Question: {question}\n\n"
        "Answer:"
    )
    return _generate(prompt, 600)


# ─────────────────────────────────────────────────────────────
# Agent upgrade feature 2: Study Plan Generator
# ─────────────────────────────────────────────────────────────

def generate_study_plan(text: str, level: str = "Beginner") -> str:
    """
    Create a smart study roadmap from the uploaded academic content.
    """
    ctx = _LEVEL_CONTEXT.get(level, _LEVEL_CONTEXT["Beginner"])
    prompt = (
        f"You are an academic learning planner helping {ctx}\n\n"
        "Analyze the following academic content and create a student-friendly study plan.\n\n"
        "Your output must include:\n"
        "1. Main topics to study\n"
        "2. Recommended order of learning (easy to advanced)\n"
        "3. What to revise first\n"
        "4. Practice suggestions\n"
        "5. A short revision checklist\n\n"
        f"Academic Content:\n{text}\n\n"
        "Study Plan:"
    )
    return _generate(prompt, 700)


# ─────────────────────────────────────────────────────────────
# Agent upgrade feature 3: Difficult concepts detector
# ─────────────────────────────────────────────────────────────

def find_difficult_concepts(text: str, level: str = "Beginner") -> str:
    """
    Identify difficult concepts, weak areas, or confusion points in the content.
    """
    ctx = _LEVEL_CONTEXT.get(level, _LEVEL_CONTEXT["Beginner"])
    prompt = (
        f"You are an educational mentor helping {ctx}\n\n"
        "Read the following academic content and identify the concepts that students may find difficult.\n\n"
        "For each difficult concept, provide:\n"
        "1. The concept name\n"
        "2. Why it may be confusing\n"
        "3. A short easy explanation\n"
        "4. One tip to understand it better\n\n"
        f"Academic Content:\n{text}\n\n"
        "Difficult Concepts:"
    )
    return _generate(prompt, 700)