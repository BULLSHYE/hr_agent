from sqlalchemy.orm import Session
from fastapi import UploadFile
from models.job_descriptions import JobDescription
from utilities.jd_parser import generate_structured_jd, extract_text_from_file
from core.embeddings import generate_embedding
from core.chroma_client import add_jd
import uuid

#Input from text
async def generate_job_description_from_text(text: str, db: Session) -> dict:
    structured_jd = await generate_structured_jd(text)

    jd_db = JobDescription(**structured_jd)
    db.add(jd_db)
    db.commit()
    db.refresh(jd_db)
    jd_id = jd_db.id

    # Embed and store in Chroma
    jd_text = structured_jd.get('job_description', text)
    embedding = generate_embedding(jd_text)
    metadata = {
        "source": "ai_generated",
        "length": len(jd_text),
        "jd_id": jd_id
    }
    add_jd(str(uuid.uuid4()), embedding, metadata)
    
    return {
        "jd_id": jd_id,
        "message": "JD generated, saved, and embedded successfully",
        "structured_jd": structured_jd
    }

#Input from file
async def extract_text(file: UploadFile, db: Session) -> dict:
    file_bytes = await file.read()
    text = await extract_text_from_file(file_bytes, file.content_type, file.filename)
    print(f"Extracted text: {text}")

    structured_jd = await generate_structured_jd(text)
    jd_db = JobDescription(**structured_jd)
    db.add(jd_db)
    db.commit()
    db.refresh(jd_db)
    jd_id = jd_db.id

    # Embed and store in Chroma
    jd_text = structured_jd.get('job_description', text)
    embedding = generate_embedding(jd_text)
    metadata = {
        "source": "ai_generated",
        "length": len(jd_text),
        "jd_id": jd_id
    }
    add_jd(str(uuid.uuid4()), embedding, metadata)
    
    return {
        "jd_id": jd_id,
        "message": "JD generated, saved, and embedded successfully",
        "structured_jd": structured_jd
    }

#generate from LLM
async def generate_job_llm(text: str) -> dict:
    structured_jd = await generate_structured_jd(text)
    return structured_jd

#After Preview, save to DB
async def save_structured_jd(structured_jd: dict, db: Session) -> dict:
    jd_db = JobDescription(**structured_jd)
    db.add(jd_db)
    db.commit()
    db.refresh(jd_db)
    jd_id = jd_db.id

    jd_text = structured_jd.get('job_description', '')
    embedding = generate_embedding(jd_text)
    metadata = {
        "source": "generated",
        "length": len(jd_text),
        "jd_id": jd_id
    }
    add_jd(str(uuid.uuid4()), embedding, metadata)
    
    return {
        "jd_id": jd_id,
        "message": "JD saved and embedded successfully",
        "structured_jd": structured_jd
    }

# Fetch job for UI 
async def fetch_jd_titles(db: Session):
    jds = db.query(JobDescription).all()
    return [jd.job_role for jd in jds]

# Fetch job description by title
def get_jd_by_title(title: str, db: Session = None):
    if db is None:
        db = Session()
        close_session = True
    else:
        close_session = False
    jd = db.query(JobDescription).filter(JobDescription.job_role.ilike(f'%{title}%')).first()
    if close_session:
        db.close()
    return jd