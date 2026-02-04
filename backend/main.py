from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from sqlalchemy import inspect
from db.db import engine, Base
from dotenv import load_dotenv
from routes.user import router as auth_router
from routes.job_descriptions import router as jd_router
from routes.choose_model import router as choose_model_router
from routes.candidates import router as candidates_router
from routes.match_score import router as match_router
from routes.email import router as email_router
from core.logging import LoggingMiddleware
 

load_dotenv()
inspector = inspect(engine)
print(inspector.get_table_names())
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI HR Recruitment Agent")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(jd_router, prefix="/jd", tags=["Job Description"])
app.include_router(choose_model_router, prefix="/model", tags=["Model Selection"])
app.include_router(candidates_router, prefix="/candidates", tags=["Candidates"])
app.include_router(match_router, prefix="/match", tags=["Matching"])
app.include_router(email_router, prefix="/email", tags=["Email"])

@app.get("/")
async def root():
    #Return with datetime
    current_time = datetime.now()
    return {"message": "Hello, World!", "datetime": current_time}
