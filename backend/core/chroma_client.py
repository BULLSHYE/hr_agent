import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
jd_collection = client.get_or_create_collection(name="job_descriptions")
candidate_collection = client.get_or_create_collection(name="candidates")

# Job Description functions
def add_jd(jd_id: str, embedding: list, metadata: dict):
    jd_collection.add(
        ids=[jd_id],
        embeddings=[embedding],
        metadatas=[metadata]
    )

def search_jd(query_embedding: list, n_results=3):
    return jd_collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

def get_jd_count():
    return jd_collection.count()

def peek_jds(n=5):
    result = jd_collection.peek(limit=n)
    if 'embeddings' in result:
        del result['embeddings']
    return result

# Candidate functions
def add_candidate(candidate_id: str, embedding: list, metadata: dict):
    candidate_collection.add(
        ids=[candidate_id],
        embeddings=[embedding],
        metadatas=[metadata]
    )

def search_candidates(query_embedding: list, n_results=5, where=None):
    return candidate_collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where
    )

def get_candidate_count():
    return candidate_collection.count()

def peek_candidates(n=5):
    result = candidate_collection.peek(limit=n)
    # Remove embeddings to make it JSON serializable
    if 'embeddings' in result:
        del result['embeddings']
    return result

