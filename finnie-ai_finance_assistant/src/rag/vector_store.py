from pathlib import Path
from langchain_chroma import Chroma
from src.rag.embedder import get_embeddings
from src.core.config import load_config


def get_vector_store(persist_directory: str = "chroma_db"):
    config = load_config()
    embeddings = get_embeddings()

    Path(persist_directory).mkdir(parents=True, exist_ok=True)

    vector_store = Chroma(
        collection_name=config["rag"]["collection_name"],
        embedding_function=embeddings,
        persist_directory=persist_directory,
    )
    return vector_store