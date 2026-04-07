from src.rag.chunker import load_kb_documents, chunk_documents
from src.rag.vector_store import get_vector_store
from src.core.config import load_config


def build_index():
    config = load_config()

    kb_path = "src/data/knowledge_base/finance_kb.jsonl"
    documents = load_kb_documents(kb_path)
    chunks = chunk_documents(
        documents,
        chunk_size=config["rag"]["chunk_size"],
        chunk_overlap=config["rag"]["chunk_overlap"]
    )

    vector_store = get_vector_store()
    vector_store.add_documents(chunks)

    print(f"Loaded {len(documents)} documents")
    print(f"Created {len(chunks)} chunks")
    print("Index built successfully.")


if __name__ == "__main__":
    build_index()