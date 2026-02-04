from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Optional
from schema.job_descriptions import JobDescriptionRequest, GenerateJDRequest
from db.db import get_db
from sqlalchemy.orm import Session
from services.job_descriptions import fetch_jd_titles, generate_job_description_from_text, extract_text, generate_job_llm, save_structured_jd
from core.chroma_client import get_jd_count as chroma_get_jd_count, peek_jds
from models.job_descriptions import JobDescription

router = APIRouter()

# Upload job description via text or file
@router.post("/upload")
async def upload_job_description(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    if text:
        jd_result = await generate_job_description_from_text(text, db)
        return {"job_description": jd_result}
    elif file:
        jd_result = await extract_text(file, db)
        return {"job_description": jd_result}
    else:
        return {"error": "No input provided. Please provide either text or a file."}

# Generate job description using LLM via text 
@router.post("/generate")
async def generate_job_description(request: GenerateJDRequest):
    text = (
        f"Company Name: {request.company_name}\n"
        f"Company URL: {request.company_url}\n"
        f"Required Skills: {request.required_skills}\n"
        f"Location: {request.location}\n"
        f"Experience Range: {request.experience_range}\n"
        f"Job Role: {request.job_role}"
    )
    if request.job_description:
        text += f"\nJob Description: {request.job_description}"

    jd_generation = await generate_job_llm(text)
   
    return {"job_description": jd_generation}

# Finalize and save structured job description
@router.post("/finalize")
async def finalize_jd(structured_jd: dict, db: Session = Depends(get_db)):
    jd_result = await save_structured_jd(structured_jd, db)
    return jd_result

@router.get("/count")
async def get_jd_count():
    try:
        count = chroma_get_jd_count()
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/peek")
async def peek_jd_data(n: int = 5):
    try:
        data = peek_jds(n)
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get job description titles for UI
@router.get("/titles")
async def get_jd_titles(db: Session = Depends(get_db)):
    try:
        titles = await fetch_jd_titles(db)
        return {"titles": titles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))