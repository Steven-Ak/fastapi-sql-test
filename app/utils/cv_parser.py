import io
import json
import pdfplumber
from app.clients.llm_clients.llm_manager import get_cohere_client


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF using pdfplumber"""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        pages_text = [page.extract_text() for page in pdf.pages if page.extract_text()]
        return "\n".join(pages_text)


def parse_cv_with_llm(cv_text: str) -> dict:
    """Send CV text to Cohere and extract structured data"""
    client = get_cohere_client()

    result = client.chat(
        messages=[
            {
                "role": "user",
                "content": f"""Extract structured information from this CV. 
Return ONLY a valid JSON object with no preamble or markdown, using exactly this structure:
{{
    "summary": "brief professional summary of the candidate",
    "title": "Job title in the header, current, or most recent job title",
    "education": [
        {{
            "degree": "degree name",
            "institution": "university or school name",
            "year": "graduation year or date range"
        }}
    ],
    "experience": [
        {{
            "title": "job title",
            "company": "company name",
            "duration": "date range e.g. 2020 - 2023"
        }}
    ],
    "technical_skills": ["skill1", "skill2"]
}}

CV Text:
{cv_text[:8000]}"""
            }
        ],
        temperature=0.1,
        max_tokens=1000,
    )

    try:
        text = result["text"].strip().replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception:
        return {
            "summary": "",
            "title": "",
            "education": [],
            "experience": [],
            "technical_skills": [],
        }