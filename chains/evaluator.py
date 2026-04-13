from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from typing import Optional


# Define Output Schema
class Evaluation(BaseModel):
    score: int = Field(description="Score from 0 to 10")
    strengths: str = Field(description="What was good")
    improvements: str = Field(description="What to improve")
    correct_answer: str = Field(description="Ideal answer")


# Parser
parser = JsonOutputParser(pydantic_object=Evaluation)


# Prompt
EVALUATOR_PROMPT = """You are an expert technical interviewer evaluating a candidate.

Question: {question}
Answer: {answer}

IMPORTANT:
- Return ONLY valid JSON
- Do NOT include explanations
- Do NOT include markdown
- Do NOT include text outside JSON

{format_instructions}
"""


prompt = ChatPromptTemplate.from_template(EVALUATOR_PROMPT)


# Chain
def create_evaluator_chain(
    model_name: str = "llama-3.1-8b-instant",
    temperature: float = 0.2,
    api_key: Optional[str] = None,
):
    llm = ChatGroq(
        model=model_name,
        temperature=temperature,
        api_key=api_key
    )

    chain = prompt | llm | parser

    return chain
