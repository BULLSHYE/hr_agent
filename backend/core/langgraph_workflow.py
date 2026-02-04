"""
LangGraph Workflow for Job Description Generation

This module implements a workflow for generating job descriptions using LangGraph.
The workflow follows these steps:
1. Extract company information from provided text
2. Generate job requirements based on skills
3. Compile a complete job description

This demonstrates a simpler LangGraph workflow focused on content generation.
"""

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from typing import TypedDict, Optional
import logging

from core.llm import get_llm

# Configure logging
logger = logging.getLogger(__name__)


class JDState(TypedDict):
    """
    State object for job description generation workflow.

    Attributes:
        company_info (str): Raw company information text
        skills (str): Required skills for the position
        requirements (str): Generated job requirements
        final_jd (str): Complete compiled job description
        errors (list): List of errors encountered during processing
    """
    company_info: str
    skills: str
    requirements: Optional[str]
    final_jd: Optional[str]
    errors: list


def extract_company_info(state: JDState) -> dict:
    """
    Node: Extract structured company information from raw text.

    Args:
        state: Current workflow state

    Returns:
        Updated state with processed company_info
    """
    try:
        logger.info("Extracting company information")
        llm = get_llm()

        prompt = f"""Extract and structure the following company information into a clear, professional format:

{state['company_info']}

Please provide:
- Company name
- Industry/sector
- Company size (if mentioned)
- Key values or culture
- Any other relevant details

Format the response as a structured paragraph."""

        response = llm.invoke([HumanMessage(content=prompt)])
        processed_info = response.content.strip()

        logger.info("Company information extracted successfully")
        return {"company_info": processed_info, "errors": state.get("errors", [])}

    except Exception as e:
        error_msg = f"Failed to extract company information: {str(e)}"
        logger.error(error_msg)
        return {"company_info": state["company_info"], "errors": state.get("errors", []) + [error_msg]}


def generate_requirements(state: JDState) -> dict:
    """
    Node: Generate detailed job requirements based on skills.

    Args:
        state: Current workflow state

    Returns:
        Updated state with generated requirements
    """
    try:
        logger.info("Generating job requirements")
        llm = get_llm()

        prompt = f"""Based on these required skills, generate comprehensive job requirements:

Skills: {state['skills']}

Please generate:
1. Technical requirements (must-have skills)
2. Experience level requirements
3. Educational background
4. Soft skills and competencies
5. Any certifications or qualifications

Structure the requirements clearly with bullet points."""

        response = llm.invoke([HumanMessage(content=prompt)])
        requirements = response.content.strip()

        logger.info("Job requirements generated successfully")
        return {"requirements": requirements, "errors": state.get("errors", [])}

    except Exception as e:
        error_msg = f"Failed to generate requirements: {str(e)}"
        logger.error(error_msg)
        return {"requirements": None, "errors": state.get("errors", []) + [error_msg]}


def compile_jd(state: JDState) -> dict:
    """
    Node: Compile a complete job description from all components.

    Args:
        state: Current workflow state

    Returns:
        Updated state with final job description
    """
    try:
        logger.info("Compiling final job description")
        llm = get_llm()

        if not state.get("requirements"):
            error_msg = "No requirements available for JD compilation"
            logger.error(error_msg)
            return {"final_jd": None, "errors": state.get("errors", []) + [error_msg]}

        prompt = f"""Compile a complete, professional job description using the following information:

COMPANY INFORMATION:
{state['company_info']}

JOB REQUIREMENTS:
{state['requirements']}

Please create a comprehensive job description that includes:
1. Company overview
2. Position summary
3. Key responsibilities
4. Required qualifications and skills
5. What we offer (benefits, growth opportunities)
6. How to apply

Make it engaging, professional, and compelling for potential candidates."""

        response = llm.invoke([HumanMessage(content=prompt)])
        final_jd = response.content.strip()

        logger.info("Job description compiled successfully")
        return {"final_jd": final_jd, "errors": state.get("errors", [])}

    except Exception as e:
        error_msg = f"Failed to compile job description: {str(e)}"
        logger.error(error_msg)
        return {"final_jd": None, "errors": state.get("errors", []) + [error_msg]}


# Build the workflow graph
logger.info("Building JD generation workflow graph")

workflow = StateGraph(JDState)

# Add nodes
workflow.add_node("extract_company", extract_company_info)
workflow.add_node("generate_requirements", generate_requirements)
workflow.add_node("compile_jd", compile_jd)

# Define edges
workflow.set_entry_point("extract_company")
workflow.add_edge("extract_company", "generate_requirements")
workflow.add_edge("generate_requirements", "compile_jd")
workflow.add_edge("compile_jd", END)

# Compile the graph
app = workflow.compile()
logger.info("JD generation workflow graph compiled successfully")


def generate_jd_with_langgraph(company_info: str, skills: str) -> Optional[str]:
    """
    Generate a complete job description using the LangGraph workflow.

    Args:
        company_info: Raw company information text
        skills: Required skills for the position

    Returns:
        Complete job description or None if generation failed
    """
    if not company_info or not company_info.strip():
        raise ValueError("Company information cannot be empty")

    if not skills or not skills.strip():
        raise ValueError("Skills cannot be empty")

    logger.info("Starting JD generation workflow")

    initial_state = {
        "company_info": company_info.strip(),
        "skills": skills.strip(),
        "requirements": None,
        "final_jd": None,
        "errors": []
    }

    try:
        result = app.invoke(initial_state)

        if result.get("errors"):
            logger.warning(f"JD generation completed with errors: {result['errors']}")

        if result.get("final_jd"):
            logger.info("JD generation workflow completed successfully")
            return result["final_jd"]
        else:
            logger.error("JD generation failed - no final JD produced")
            return None

    except Exception as e:
        error_msg = f"JD generation workflow failed: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def get_jd_workflow_status() -> dict:
    """
    Get current status and metadata of the JD generation workflow.

    Returns:
        Dictionary with workflow information
    """
    return {
        "nodes": ["extract_company", "generate_requirements", "compile_jd"],
        "entry_point": "extract_company",
        "end_point": "END",
        "description": "AI-powered job description generation workflow",
        "capabilities": [
            "Company information extraction",
            "Requirements generation from skills",
            "Professional JD compilation"
        ]
    }