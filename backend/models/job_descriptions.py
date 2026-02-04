from sqlalchemy import Column, Integer, String, Text, DateTime
from db.db import Base

class JobDescription(Base):
    __tablename__ = 'job_descriptions'

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String)
    company_url = Column(String)
    required_skills = Column(Text)
    location = Column(String)
    experience_range = Column(String)
    job_role = Column(String)
    job_description = Column(Text)
    hr_email = Column(String)