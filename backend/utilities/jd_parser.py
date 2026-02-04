import json
from langchain_core.messages import SystemMessage, HumanMessage
import fitz
import docx
from io import BytesIO
from core.llm import get_llm

# Extract text from uploaded file based on content type
async def extract_text_from_file(file_bytes: bytes, content_type: str, filename: str = None) -> str:
    # Determine content type from filename if not provided
    if not content_type and filename:
        if filename.lower().endswith('.pdf'):
            content_type = "application/pdf"
        elif filename.lower().endswith('.docx'):
            content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        else:
            raise ValueError(f"Unsupported file type based on filename: {filename}")
    
    if content_type == "application/pdf":
        pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
        return "".join(page.get_text() for page in pdf_document)

    elif content_type == (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ):
        doc = docx.Document(BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs)

    else:
        raise ValueError(f"Unsupported file type: {content_type}")

# Generate structured job description from text using LLM    
async def generate_structured_jd(text: str) -> dict:
    prompt = f"""
    Based on the following job details, generate a professional and comprehensive job description. Return ONLY valid JSON with these exact fields:
    - company_name: string
    - company_url: string
    - required_skills: string (comma-separated)
    - location: string
    - experience_range: string
    - job_role: string
    - job_description: string (a full, detailed, and engaging job description text based on all the provided information, including responsibilities, requirements, benefits, etc.)
    - hr_email: string (use hr@company.com as default if not specified)

    Job Details:
    {text}

    Ensure the job_description is compelling, professional, and includes all relevant details from the provided information. Make it at least 300 words long with proper structure.
    Return only the JSON, no additional text or explanations.
    """
    llm = get_llm()
    messages = [
        SystemMessage(content="You are an expert HR assistant that creates professional job descriptions. Always respond with valid JSON only."),
        HumanMessage(content=prompt)
    ]
    response = await llm.ainvoke(messages)
    result = response.content.strip()
    
    if result.startswith('```json'):
        result = result[7:]
    if result.endswith('```'):
        result = result[:-3]
    result = result.strip()
    try:
        data = json.loads(result)
        return data
    except:
        # Fallback: and create a basic JD manually
        lines = text.split('\n')
        info = {}
        for line in lines:
            if ': ' in line:
                key, value = line.split(': ', 1)
                key = key.lower().replace(' ', '_')
                info[key] = value
        
        basic_jd = f"""
        Join {info.get('company_name', 'our company')} as a {info.get('job_role', 'professional')}.

        We are looking for candidates with {info.get('experience_range', 'relevant')} years of experience and skills in {info.get('required_skills', 'various areas')}.

        Location: {info.get('location', 'TBD')}

        Responsibilities and requirements will be discussed during the interview process.
        """
        return {
            "company_name": info.get('company_name', ''),
            "company_url": info.get('company_url', ''),
            "required_skills": info.get('required_skills', ''),
            "location": info.get('location', ''),
            "experience_range": info.get('experience_range', ''),
            "job_role": info.get('job_role', ''),
            "job_description": basic_jd.strip(),
            "hr_email": "hr@example.com"
        }