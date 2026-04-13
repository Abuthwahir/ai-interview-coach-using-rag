from langchain_core.documents import Document


def create_vector_store(documents):
    # Just return documents directly (no DB)
    return documents


def create_retriever(documents):
    def retrieve(query):
        # simple keyword-based filtering
        return [
            doc for doc in documents
            if query.lower() in doc.page_content.lower()
        ][:3]

    return retrieve