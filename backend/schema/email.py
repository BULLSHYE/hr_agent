from pydantic import BaseModel

class SendEmailsRequest(BaseModel):
    title: str
    candidate_name: str
    candidate_email: str
    score: int
    reason: str