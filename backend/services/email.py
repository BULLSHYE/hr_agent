from core.llm import get_llm
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

load_dotenv()
# Real email service using SMTP
def send_email(to_email: str, subject: str, body: str):
    from_email = os.getenv('SMTP_USERNAME')
    password = os.getenv('SMTP_PASSWORD')
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Generate candidate email using LLM
async def generate_candidate_email(candidate_name: str, job_role: str, company_name: str) -> str:
    prompt = f"""
    Generate a professional, personalized email to inform a candidate that they have been shortlisted for a job interview.

    Candidate Name: {candidate_name}
    Job Role: {job_role}
    Company: {company_name}

    Email should:
    - Congratulate them
    - Mention the job role and company
    - Provide next steps (e.g., interview details)
    - Be encouraging and professional

    Write the email body only.
    """
    llm = get_llm()
    messages = [
        SystemMessage(content="You are an HR assistant generating professional emails."),
        HumanMessage(content=prompt)
    ]
    response = await llm.ainvoke(messages)
    return response.content.strip()

# Generate HR email summarizing shortlisted candidate
async def generate_hr_email(candidate_name: str, job_role: str, score: int, reason: str) -> str:
    prompt = f"""
    Generate a professional email to HR summarizing a shortlisted candidate.

    Candidate Name: {candidate_name}
    Job Role: {job_role}
    Match Score: {score}%
    Reasoning: {reason}

    Email should:
    - Summarize the candidate's fit
    - Include score and key reasons
    - Suggest next steps

    Write the email body only.
    """
    llm = get_llm()
    messages = [
        SystemMessage(content="You are an HR assistant generating professional emails."),
        HumanMessage(content=prompt)
    ]
    response = await llm.ainvoke(messages)
    return response.content.strip()
