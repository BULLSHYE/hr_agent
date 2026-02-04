from fastapi import APIRouter, HTTPException, Depends
from services.match_score import match_jd_to_candidates
from schema.match_score import ScoreRequest
from db.db import get_db
from sqlalchemy.orm import Session

router = APIRouter()

# Endpoint to score candidates against a job description
@router.post("/score")
async def score_candidates(request: ScoreRequest, db: Session = Depends(get_db)):
    try:
        matches = await match_jd_to_candidates(request.title, request.n_results, db)
        return {"matches": matches}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))