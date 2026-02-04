"""
LangGraph Workflow for AI-Powered HR Recruitment Agent

This module implements the core recruitment workflow using LangGraph.
The workflow follows these steps:
1. Embed the job description
2. Retrieve similar candidates from vector database
3. Match and score candidates against the JD
4. Generate personalized emails for top candidates

The workflow uses a state-based approach where each node modifies
the shared state dictionary and passes it to the next node.
"""

from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
import logging

from core.embeddings import generate_embedding
from core.chroma_client import search_candidates
from services.match_score import cosine_similarity, generate_reason
from services.email import generate_candidate_email, generate_hr_email

# Configure logging
logger = logging.getLogger(__name__)


# -------------------------
# STATE DEFINITION
# -------------------------

class AgentState(TypedDict):
    """
    State object for the recruitment workflow.

    Attributes:
        jd_text (str): Raw job description text
        jd_embedding (list): Vector embedding of the job description
        candidates (list): List of candidate dictionaries from vector search
        matches (list): List of matched candidates with scores and reasons
        candidate_email (str): Generated email for the top candidate
        hr_email (str): Generated notification email for HR
        errors (list): List of errors encountered during processing
    """
    jd_text: str
    jd_embedding: Optional[List[float]]
    candidates: List[Dict[str, Any]]
    matches: List[Dict[str, Any]]
    candidate_email: Optional[str]
    hr_email: Optional[str]
    errors: List[str]


# -------------------------
# NODES
# -------------------------

def embed_jd(state: AgentState) -> Dict[str, Any]:
    """
    Node: Generate embedding for the job description.

    Args:
        state: Current workflow state

    Returns:
        Updated state with jd_embedding
    """
    try:
        logger.info("Generating embedding for job description")
        embedding = generate_embedding(state["jd_text"])
        logger.info(f"Generated embedding with dimension: {len(embedding)}")
        return {"jd_embedding": embedding, "errors": state.get("errors", [])}
    except Exception as e:
        error_msg = f"Failed to generate JD embedding: {str(e)}"
        logger.error(error_msg)
        return {"jd_embedding": None, "errors": state.get("errors", []) + [error_msg]}


def retrieve_candidates(state: AgentState) -> Dict[str, Any]:
    """
    Node: Retrieve similar candidates from vector database.

    Args:
        state: Current workflow state

    Returns:
        Updated state with candidates list
    """
    if not state.get("jd_embedding"):
        error_msg = "No JD embedding available for candidate retrieval"
        logger.error(error_msg)
        return {"candidates": [], "errors": state.get("errors", []) + [error_msg]}

    try:
        logger.info("Searching for similar candidates in vector database")
        results = search_candidates(state["jd_embedding"], n_results=5)

        # Extract candidates from ChromaDB results
        ids = results.get("ids", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        embeddings = results.get("embeddings", [[]])[0]

        candidates = []
        for i in range(len(ids)):
            candidates.append({
                "id": ids[i],
                "metadata": metadatas[i],
                "embedding": embeddings[i]
            })

        logger.info(f"Retrieved {len(candidates)} candidates")
        return {"candidates": candidates, "errors": state.get("errors", [])}

    except Exception as e:
        error_msg = f"Failed to retrieve candidates: {str(e)}"
        logger.error(error_msg)
        return {"candidates": [], "errors": state.get("errors", []) + [error_msg]}


def match_and_score(state: AgentState) -> Dict[str, Any]:
    """
    Node: Match candidates against JD and generate scores with reasoning.

    Args:
        state: Current workflow state

    Returns:
        Updated state with matches list
    """
    if not state.get("jd_embedding"):
        error_msg = "No JD embedding available for matching"
        logger.error(error_msg)
        return {"matches": [], "errors": state.get("errors", []) + [error_msg]}

    if not state.get("candidates"):
        error_msg = "No candidates available for matching"
        logger.error(error_msg)
        return {"matches": [], "errors": state.get("errors", []) + [error_msg]}

    try:
        logger.info("Matching and scoring candidates")
        jd_embedding = state["jd_embedding"]
        matches = []

        for candidate in state["candidates"]:
            try:
                # Calculate similarity score
                sim = cosine_similarity(jd_embedding, candidate["embedding"])
                score = round(sim * 100, 2)

                # Generate AI-powered reasoning
                reason = generate_reason(
                    state["jd_text"],
                    candidate["metadata"],
                    score
                )

                matches.append({
                    "candidate_id": candidate["id"],
                    "metadata": candidate["metadata"],
                    "score": score,
                    "reason": reason
                })

            except Exception as e:
                logger.warning(f"Failed to score candidate {candidate['id']}: {str(e)}")
                continue

        # Sort by score descending
        matches.sort(key=lambda x: x["score"], reverse=True)

        logger.info(f"Generated {len(matches)} candidate matches")
        return {"matches": matches, "errors": state.get("errors", [])}

    except Exception as e:
        error_msg = f"Failed to match and score candidates: {str(e)}"
        logger.error(error_msg)
        return {"matches": [], "errors": state.get("errors", []) + [error_msg]}


def generate_emails(state: AgentState) -> Dict[str, Any]:
    """
    Node: Generate personalized emails for top candidate and HR.

    Args:
        state: Current workflow state

    Returns:
        Updated state with generated emails
    """
    if not state.get("matches"):
        error_msg = "No matches available for email generation"
        logger.error(error_msg)
        return {
            "candidate_email": None,
            "hr_email": None,
            "errors": state.get("errors", []) + [error_msg]
        }

    try:
        logger.info("Generating personalized emails")
        top_candidate = state["matches"][0]

        # Prepare email data
        email_data = {
            "candidate_name": top_candidate["metadata"].get("name", "Candidate"),
            "role": "AI Engineer",  # Could be extracted from JD
            "company": "ABC Tech",  # Could be configurable
            "score": top_candidate["score"],
            "reason": top_candidate["reason"]
        }

        # Generate emails
        candidate_email = generate_candidate_email(email_data)
        hr_email = generate_hr_email(email_data)

        logger.info("Successfully generated personalized emails")
        return {
            "candidate_email": candidate_email,
            "hr_email": hr_email,
            "errors": state.get("errors", [])
        }

    except Exception as e:
        error_msg = f"Failed to generate emails: {str(e)}"
        logger.error(error_msg)
        return {
            "candidate_email": None,
            "hr_email": None,
            "errors": state.get("errors", []) + [error_msg]
        }


# -------------------------
# GRAPH
# -------------------------

def build_graph() -> Any:
    """
    Build and compile the recruitment workflow graph.

    Returns:
        Compiled LangGraph workflow
    """
    logger.info("Building recruitment workflow graph")

    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("embed_jd", embed_jd)
    graph.add_node("retrieve_candidates", retrieve_candidates)
    graph.add_node("match_and_score", match_and_score)
    graph.add_node("generate_emails", generate_emails)

    # Define edges
    graph.set_entry_point("embed_jd")
    graph.add_edge("embed_jd", "retrieve_candidates")
    graph.add_edge("retrieve_candidates", "match_and_score")
    graph.add_edge("match_and_score", "generate_emails")
    graph.add_edge("generate_emails", END)

    compiled_graph = graph.compile()
    logger.info("Recruitment workflow graph compiled successfully")

    return compiled_graph


# -------------------------
# RUNNER
# -------------------------

agent_graph = build_graph()

def run_agent(jd_text: str) -> Dict[str, Any]:
    """
    Execute the recruitment workflow for a given job description.

    Args:
        jd_text: Raw job description text

    Returns:
        Final workflow state with results
    """
    if not jd_text or not jd_text.strip():
        raise ValueError("Job description text cannot be empty")

    logger.info("Starting recruitment workflow execution")

    initial_state = {
        "jd_text": jd_text.strip(),
        "jd_embedding": None,
        "candidates": [],
        "matches": [],
        "candidate_email": None,
        "hr_email": None,
        "errors": []
    }

    try:
        result = agent_graph.invoke(initial_state)
        logger.info("Recruitment workflow completed successfully")

        # Log any errors that occurred
        if result.get("errors"):
            logger.warning(f"Workflow completed with {len(result['errors'])} errors: {result['errors']}")

        return result

    except Exception as e:
        error_msg = f"Workflow execution failed: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


# -------------------------
# UTILITY FUNCTIONS
# -------------------------

def get_workflow_status() -> Dict[str, Any]:
    """
    Get current status and statistics of the workflow.

    Returns:
        Dictionary with workflow metadata
    """
    return {
        "nodes": ["embed_jd", "retrieve_candidates", "match_and_score", "generate_emails"],
        "entry_point": "embed_jd",
        "end_point": "END",
        "description": "AI-powered recruitment matching workflow"
    }
    jd_embedding = state["jd_embedding"]
    matches = []

    for c in state["candidates"]:
        sim = cosine_similarity(jd_embedding, c["embedding"])
        score = round(sim * 100, 2)

        reason = generate_reason(
            state["jd_text"],
            c["metadata"],
            score
        )

        matches.append({
            "candidate_id": c["id"],
            "metadata": c["metadata"],
            "score": score,
            "reason": reason
        })

    return {"matches": matches}


def generate_emails(state: AgentState):
    top_candidate = state["matches"][0]

    data = {
        "candidate_name": top_candidate["metadata"].get("name"),
        "role": "AI Engineer",
        "company": "ABC Tech",
        "score": top_candidate["score"],
        "reason": top_candidate["reason"]
    }

    candidate_email = _generate_candidate_email(data)
    hr_email = _generate_hr_email(data)

    return {
        "candidate_email": candidate_email,
        "hr_email": hr_email
    }


# -------------------------
# GRAPH
# -------------------------

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("embed_jd", embed_jd)
    graph.add_node("retrieve_candidates", retrieve_candidates)
    graph.add_node("match_and_score", match_and_score)
    graph.add_node("generate_emails", generate_emails)

    graph.set_entry_point("embed_jd")
    graph.add_edge("embed_jd", "retrieve_candidates")
    graph.add_edge("retrieve_candidates", "match_and_score")
    graph.add_edge("match_and_score", "generate_emails")
    graph.add_edge("generate_emails", END)

    return graph.compile()


# -------------------------
# RUNNER
# -------------------------

agent_graph = build_graph()

def run_agent(jd_text: str) -> Dict[str, Any]:
    """
    Execute the recruitment workflow for a given job description.

    Args:
        jd_text: Raw job description text

    Returns:
        Final workflow state with results
    """
    if not jd_text or not jd_text.strip():
        raise ValueError("Job description text cannot be empty")

    logger.info("Starting recruitment workflow execution")

    initial_state = {
        "jd_text": jd_text.strip(),
        "jd_embedding": None,
        "candidates": [],
        "matches": [],
        "candidate_email": None,
        "hr_email": None,
        "errors": []
    }

    try:
        result = agent_graph.invoke(initial_state)
        logger.info("Recruitment workflow completed successfully")

        # Log any errors that occurred
        if result.get("errors"):
            logger.warning(f"Workflow completed with {len(result['errors'])} errors: {result['errors']}")

        return result

    except Exception as e:
        error_msg = f"Workflow execution failed: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


# -------------------------
# UTILITY FUNCTIONS
# -------------------------

def get_workflow_status() -> Dict[str, Any]:
    """
    Get current status and statistics of the workflow.

    Returns:
        Dictionary with workflow metadata
    """
    return {
        "nodes": ["embed_jd", "retrieve_candidates", "match_and_score", "generate_emails"],
        "entry_point": "embed_jd",
        "end_point": "END",
        "description": "AI-powered recruitment matching workflow"
    }
