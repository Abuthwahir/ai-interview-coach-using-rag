from langchain.memory import ConversationBufferMemory
from langchain_core.chat_history import InMemoryChatMessageHistory


def create_memory():
    """Create conversation memory for interview."""
    return ConversationBufferMemory(
        memory_key="history",
        return_messages=True,
        chat_memory=InMemoryChatMessageHistory()
    )