from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from services.email import send_email, generate_candidate_email, generate_hr_email
from services.job_descriptions import get_jd_by_title
from schema.email import SendEmailsRequest
from db.db import get_db
from sqlalchemy.orm import Session

router = APIRouter()

# Background task to send emails
async def send_emails_background(candidate_email: str, candidate_subject: str, candidate_body: str, hr_email: str, hr_subject: str, hr_body: str):
    """Background task to send emails"""
    try:
        send_email(candidate_email, candidate_subject, candidate_body)
        if hr_email:
            send_email(hr_email, hr_subject, hr_body)
    except Exception as e:
        # In a real app, you'd log this error
        print(f"Error sending emails: {e}")

# Endpoint to send shortlist emails
@router.post("/send-emails")
async def send_shortlist_emails(request: SendEmailsRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if request.score <= 60:
        raise HTTPException(status_code=400, detail="Candidate score must be greater than 60 to send emails")
    
    jd = get_jd_by_title(request.title, db)
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    try:
        # Generate emails
        candidate_body = await generate_candidate_email(request.candidate_name, jd.job_role, jd.company_name)
        hr_body = await generate_hr_email(request.candidate_name, jd.job_role, request.score, request.reason)
        
        # Send emails asynchronously with BackgroundTasks
        candidate_subject = f"Congratulations! You're Shortlisted for {jd.job_role}"
        hr_subject = f"Shortlisted Candidate: {request.candidate_name} for {jd.job_role}"
        
        background_tasks.add_task(
            send_emails_background,
            request.candidate_email,
            candidate_subject,
            candidate_body,
            jd.hr_email,
            hr_subject,
            hr_body
        )
        
        return {"message": "Emails queued for sending in background"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))