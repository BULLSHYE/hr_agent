from pydantic import BaseModel

class ScoreRequest(BaseModel):
    title: str
    n_results: int = 5