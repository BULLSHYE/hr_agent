from utilities.mock_sources import fetch_linkedin, fetch_naukri
from core.embeddings import generate_embedding
from core.chroma_client import add_candidate, search_candidates
import uuid
import json
from langchain_core.messages import SystemMessage, HumanMessage
from core.llm import get_llm

# Fetch candidates from multiple external sources
def fetch_candidates_from_sources():
    sources = [fetch_linkedin]
    # sources = [fetch_linkedin, fetch_naukri]
    all_candidates = []
    for source in sources:
        candidates = source()
        all_candidates.extend(candidates)
    return all_candidates

# Store candidates embeddings in ChromaDB
def store_candidates_embeddings(candidates: list):
    for candidate in candidates:
        exp_str = candidate['experience']
        exp_num = int(exp_str.split()[0]) if exp_str else 0
        candidate_text = f"{candidate['name']} skills: {', '.join(candidate['skills'])} experience: {candidate['experience']} years"
        embedding = generate_embedding(candidate_text)
        candidate_id = str(uuid.uuid4())
        metadata = {
            "name": candidate['name'],
            "skills": ', '.join(candidate['skills']),
            "experience": exp_num,
            "experience_str": exp_str,
            "email": candidate['email']
        }
        add_candidate(candidate_id, embedding, metadata)

# Job description search to find matching candidates
async def parse_search_query(query: str):
    prompt = f"""
    Parse the following search query for candidates into structured data.
    Identify and extract:
    - skills: list of programming languages, frameworks, tools, or technical skills mentioned (e.g., Python, Java, React)
    - min_experience: minimum years of experience if specified (e.g., 3 years -> 3), else None
    - other_requirements: any other non-skill requirements like location, role, etc.

    Query: {query}

    Return ONLY valid JSON with keys: skills (list), min_experience (int or null), other_requirements (string).
    Example: {{"skills": ["Python", "Machine Learning"], "min_experience": 3, "other_requirements": "remote"}}
    """
    llm = get_llm()
    messages = [
        SystemMessage(content="You are a helpful assistant that parses search queries into structured data. Always respond with valid JSON only."),
        HumanMessage(content=prompt)
    ]
    response = await llm.ainvoke(messages)
    result = response.content.strip()
    # Remove markdown if present
    if result.startswith('```json'):
        result = result[7:]
    if result.endswith('```'):
        result = result[:-3]
    result = result.strip()
    try:
        parsed = json.loads(result)
        return parsed
    except:
        # Fallback: simple parsing
        skills = []
        min_exp = None
        other = query
        words = query.lower().split()
        known_skills = ['python', 'java', 'react', 'javascript', 'typescript', 'machine learning', 'ml', 'ai', 'data science', 'aws', 'spring boot', 'microservices', 'pandas', 'scikit-learn', 'redux', 'ui/ux']
        for word in words:
            if word in known_skills:
                skills.append(word.capitalize() if word != 'ml' else 'Machine Learning')
            elif word.isdigit():
                min_exp = int(word)
        return {"skills": skills, "min_experience": min_exp, "other_requirements": other}

# Search candidates based on parsed query
async def search_candidates_by_query(query: str, n_results=5):
    parsed = await parse_search_query(query)
    query_embedding = generate_embedding(query)
    print("Parsed Query:", parsed, "Embedding Length:", len(query_embedding))
    results = search_candidates(query_embedding, n_results * 2)  # get more to filter
    # Filter results based on parsed skills
    filtered_results = {'ids': [[]], 'metadatas': [[]], 'distances': [[]]}
    if results['ids']:
        ids = results['ids'][0]
        metadatas = results['metadatas'][0]
        distances = results['distances'][0] if 'distances' in results and results['distances'] else [None] * len(ids)
        for i in range(len(ids)):
            metadata = metadatas[i]
            skills = metadata['skills'].lower()
            include = True
            if parsed.get('skills'):
                if not any(skill.lower() in skills for skill in parsed['skills']):
                    include = False
            if include:
                filtered_results['ids'][0].append(ids[i])
                filtered_results['metadatas'][0].append(metadatas[i])
                filtered_results['distances'][0].append(distances[i])
                if len(filtered_results['ids'][0]) >= n_results:
                    break
    return filtered_results
