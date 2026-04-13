from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from typing import Optional

# Updated Prompt
INTERVIEWER_SYSTEM_PROMPT = """You are an expert technical interviewer.

Your role:
- Ask one clear, focused question at a time
- Reference previous answers when relevant
- Build on the conversation naturally
- Be professional but encouraging

Interview type: {interview_type}
Position level: {level}
Focus area: {focus_area}

Remember: You have access to the full conversation history.
Use it to avoid repeating questions and to ask follow-ups.
"""


def create_interviewer_chain_with_memory(
    memory,
    model_name: str = "llama-3.1-8b-instant",
    temperature: float = 0.7,
    api_key: Optional[str] = None,
):
    """Create interviewer chain with memory."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", INTERVIEWER_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])

    llm = ChatGroq(
        model=model_name,
        temperature=temperature,
        api_key=api_key
    )

    chain = (
        RunnablePassthrough.assign(
            history=lambda x: memory.chat_memory.messages
        )
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain
