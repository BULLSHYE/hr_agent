from pydantic import BaseModel
from typing import List, Optional

class Candidate(BaseModel):
    name: str
    experience: str
    skills: List[str]
    current_role: Optional[str] = None
    education: Optional[str] = None
    location: Optional[str] = None
    resume_summary: Optional[str] = None
    email: str

class StoreRequest(BaseModel):
    candidates: Optional[List[Candidate]] = None