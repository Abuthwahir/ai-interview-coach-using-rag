from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from typing import Optional


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def create_question_generator(
    retriever,
    model_name: str = "llama-3.1-8b-instant",
    temperature: float = 0.7,
    api_key: Optional[str] = None,
):
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert technical interviewer.

Generate a question based on job requirements below.

{context}
"""),
        ("human", """Generate a {difficulty} level question about {topic}.

Previous questions: {previous_questions}
""")
    ])

    llm = ChatGroq(
        model=model_name,
        temperature=temperature,
        api_key=api_key
    )

    chain = (
        {
            "context": lambda x: format_docs(retriever(x["topic"])),
            "difficulty": lambda x: x["difficulty"],
            "topic": lambda x: x["topic"],
            "previous_questions": lambda x: x.get("previous_questions", "None")
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain
