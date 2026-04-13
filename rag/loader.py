from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path


def load_job_description(file_path: str):
    loader = TextLoader(file_path)
    docs = loader.load()

    for doc in docs:
        doc.metadata['source'] = Path(file_path).name

    return docs


def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=30
    )
    return splitter.split_documents(documents)