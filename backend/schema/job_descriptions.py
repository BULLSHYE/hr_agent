from pydantic import BaseModel
from typing import Optional
from fastapi import UploadFile

class JobDescriptionRequest(BaseModel):
    text: Optional[str] = None
    file: Optional[UploadFile] = None

class GenerateJDRequest(BaseModel):
    company_name: str
    company_url: str
    required_skills: str
    location: str
    experience_range: str
    job_role: str
    job_description: Optional[str] = None