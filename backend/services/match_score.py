from core.chroma_client import search_candidates
from core.embeddings import generate_embedding
from core.llm import get_llm
from services.job_descriptions import get_jd_by_title
from langchain_core.messages import SystemMessage, HumanMessage
from sqlalchemy.orm import Session
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Match job description to candidates and generate match scores with explanations
def cosine_similarity(vec1, vec2):
    """
    Calculate cosine similarity between two vectors.

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Similarity score between 0 and 1
    """
    vec1 = np.array(vec1).reshape(1, -1)
    vec2 = np.array(vec2).reshape(1, -1)
    return cosine_similarity(vec1, vec2)[0][0]

# Generate match score and reason for a candidate against a job description
async def generate_reason(jd_text: str, candidate_metadata: dict, score: float) -> str:
    """
    Generate a human-readable reason for the match score.

    Args:
        jd_text: Job description text
        candidate_metadata: Candidate information
        score: Match score (0-100)

    Returns:
        Explanation string
    """
    try:
        candidate_text = f"Name: {candidate_metadata.get('name', 'Unknown')}, Skills: {candidate_metadata.get('skills', 'Not specified')}, Experience: {candidate_metadata.get('experience', 'Not specified')}"

        prompt = f"""
        Explain why this candidate received a match score of {score}% for the following job.

        Job Description: {jd_text[:500]}...  # Truncated for brevity

        Candidate: {candidate_text}

        Provide a brief, professional explanation (2-3 sentences) of the match quality.
        """

        llm = get_llm()
        messages = [
            SystemMessage(content="You are an HR assistant explaining candidate-job matches."),
            HumanMessage(content=prompt)
        ]
        response = await llm.ainvoke(messages)
        return response.content.strip()

    except Exception as e:
        return f"Match score of {score}% based on skills and experience alignment."

# Main function to match job description to candidates and generate scores
async def match_jd_to_candidates(title: str, n_results=5, db: Session = None) -> list:
    jd = get_jd_by_title(title, db)
    if not jd:
        raise ValueError(f"Job description with title containing '{title}' not found")
    
    jd_text = jd.job_description
    # Find matching candidates
    jd_embedding = generate_embedding(jd_text)
    candidate_results = search_candidates(jd_embedding, n_results)

    matches = []
    if candidate_results['ids']:
        ids = candidate_results['ids'][0]
        metadatas = candidate_results['metadatas'][0]
        distances = candidate_results['distances'][0] if 'distances' in candidate_results and candidate_results['distances'] else [None] * len(ids)
        for i in range(len(ids)):
            candidate_metadata = metadatas[i]
            score, reason = await generate_match_score(jd_text, candidate_metadata)
            matches.append({
                "candidate_id": ids[i],
                "name": candidate_metadata['name'],
                "skills": candidate_metadata['skills'],
                "experience": candidate_metadata['experience'],
                "email": candidate_metadata['email'],
                "score": score,
                "reason": reason
            })

    return matches

# Generate match score and reason for a candidate against a job description
async def generate_match_score(jd_text: str, candidate_metadata: dict) -> tuple[int, str]:
    candidate_text = f"Name: {candidate_metadata['name']}, Skills: {candidate_metadata['skills']}, Experience: {candidate_metadata['experience']} years"
    prompt = f"""
    Compare the following job description with the candidate profile.
    Generate a match score from 0 to 100, and provide a brief explanation.

    Job Description: {jd_text}

    Candidate: {candidate_text}

    Return in format: Score: X% Reason: explanation
    """
    llm = get_llm()
    messages = [
        SystemMessage(content="You are an HR assistant that evaluates candidate-job matches."),
        HumanMessage(content=prompt)
    ]
    response = await llm.ainvoke(messages)
    result = response.content.strip()
    # Parse score and reason
    try:
        score_part, reason_part = result.split("Reason:", 1)
        score = int(score_part.replace("Score:", "").replace("%", "").strip())
        reason = reason_part.strip()
    except:
        score = 50
        reason = result
    return score, reason