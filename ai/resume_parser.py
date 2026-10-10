import json
import os
import re
from pathlib import Path

import pymupdf
from docx import Document
from google import genai

MODEL_NAME = "gemini-3.5-flash-lite"
MAX_CHARS = 4000

PROMPT_TEMPLATE = """
Extract ALL information from the resume below that could be useful for a hiring decision.

Return only valid JSON with this structure:
{
  "name": null,
  "email": null,
  "phone": null,
  "summary": null,
  "skills": [],
  "education": [],
  "experience": [],
  "projects": [],
  "certifications": [],
  "additional_info": {}
}

Rules:
- Use "additional_info" for any other important detail that does not fit the keys above, such as positions of responsibility, achievements, hackathons, events, awards, publications, languages, volunteering. Create a clear key name for each group.
- Extract only information supported by the resume.
- Do not invent missing details.
- Identify skills from the resume itself; do not use a fixed skill list.
- Do not leave out any section of the resume.
- Use null for unavailable scalar fields and [] for unavailable lists.

Resume:
{resume_text}
"""


def extract_resume_text(file_path):
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if file_path.suffix.lower() == ".pdf":
        with pymupdf.open(file_path) as pdf:
            text = "\n".join(page.get_text() for page in pdf)
    elif file_path.suffix.lower() == ".docx":
        document = Document(file_path)
        text = "\n".join(p.text for p in document.paragraphs)
    else:
        raise ValueError("Only PDF and DOCX files are supported.")

    if not text.strip():
        raise ValueError("No text found. The resume may be scanned.")

    return text.strip()


def clean_resume_text(text):
    return re.sub(r"\s+", " ", text).strip()


def parse_resume(file_path):
    text = clean_resume_text(extract_resume_text(file_path))[:MAX_CHARS]

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=PROMPT_TEMPLATE.replace("{resume_text}", text),
        config={
            "temperature": 0.1,
            "response_mime_type": "application/json",
        },
    )

    return json.loads(response.text)