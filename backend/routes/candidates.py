from fastapi import APIRouter, HTTPException
from services.candidates import fetch_candidates_from_sources, store_candidates_embeddings, search_candidates_by_query
from core.chroma_client import get_candidate_count, peek_candidates
from schema.candidates import StoreRequest

router = APIRouter()

# Fetch candidates from external sources mock data
@router.post("/fetch")
async def fetch_candidates():
    try:
        candidates = fetch_candidates_from_sources()
        return {"candidates": candidates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Store candidates embeddings
@router.post("/store")
async def store_candidates(request: StoreRequest):
    try:
        candidates = request.candidates if request.candidates else fetch_candidates_from_sources()
        await store_candidates_embeddings(candidates)
        return {"message": "Candidates embeddings stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/store-from-fetch")
async def store_from_fetch():
    try:
        candidates = fetch_candidates_from_sources()
        store_candidates_embeddings(candidates)
        return {"message": f"Stored {len(candidates)} candidates from sources"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Search candidates by query    
@router.get("/search")
async def search_candidates(query: str, n_results: int = 5):
    try:
        results = await search_candidates_by_query(query, n_results)
        candidates_list = []
        if results['ids']:
            ids = results['ids'][0]
            metadatas = results['metadatas'][0]
            distances = results['distances'][0] if 'distances' in results and results['distances'] else [None] * len(ids)
            for i in range(len(ids)):
                candidate = {
                    "id": ids[i],
                    "name": metadatas[i]['name'],
                    "skills": metadatas[i]['skills'],
                    "experience": metadatas[i]['experience'],
                    "email": metadatas[i]['email'],
                    "distance": distances[i]
                }
                candidates_list.append(candidate)
        return {"candidates": candidates_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/count")
async def get_candidates_count():
    try:
        count = get_candidate_count()
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/peek")
async def peek_candidates_data(n: int = 5):
    try:
        data = peek_candidates(n)
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))