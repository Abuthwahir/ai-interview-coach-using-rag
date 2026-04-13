from rag.loader import load_job_description, split_documents
from rag.retriever import create_vector_store, create_retriever
from chains.question_generator import create_question_generator
from typing import Optional


def setup_interview_rag(
    path,
    model_name: str = "llama-3.1-8b-instant",
    temperature: float = 0.7,
    api_key: Optional[str] = None,
):
    docs = load_job_description(path)
    chunks = split_documents(docs)

    vector_store = create_vector_store(chunks)
    retriever = create_retriever(vector_store)

    question_gen = create_question_generator(
        retriever,
        model_name=model_name,
        temperature=temperature,
        api_key=api_key
    )

    return question_gen
