from langchain_core.tools import tool
from typing import Literal

# Global state
interview_state = {
    "difficulty": "medium",
    "scores": [],
}


def reset_interview_state():
    """Reset adaptive interview state for a fresh session."""
    interview_state["difficulty"] = "medium"
    interview_state["scores"] = []

@tool
def get_easy_question(topic: str) -> str:
    """Get an easy question for a topic."""
    return f"Explain basics of {topic}"

@tool
def get_medium_question(topic: str) -> str:
    """Get a medium difficulty question for a topic."""
    return f"Explain how {topic} works in real applications"

@tool
def get_hard_question(topic: str) -> str:
    """Get a hard question for a topic."""
    return f"Explain advanced concepts of {topic} with system design"

@tool
def evaluate_answer(answer: str) -> dict:
    """Evaluate candidate answer and return score and average score."""
    word_count = len(answer.split())

    if word_count < 10:
        score = 3
    elif word_count < 30:
        score = 5
    elif word_count < 60:
        score = 7
    else:
        score = 9

    interview_state["scores"].append(score)

    avg = sum(interview_state["scores"]) / len(interview_state["scores"])

    return {
        "score": score,
        "avg_score": avg
    }

@tool
def get_interview_status(dummy: str = "") -> dict:
    """Get current interview status including average score."""
    
    scores = interview_state["scores"]
    avg = sum(scores) / len(scores) if scores else 0

    return {
        "avg_score": avg,
        "difficulty": interview_state["difficulty"]
    }
@tool
def set_difficulty(level: str) -> str:
    """Set interview difficulty level (easy, medium, hard)."""

    # Fix weird agent input like: level='easy'
    if "=" in level:
        level = level.split("=")[-1].strip("'\"")

    if level not in ["easy", "medium", "hard"]:
        level = "medium"

    interview_state["difficulty"] = level
    return f"Difficulty set to {level}"
