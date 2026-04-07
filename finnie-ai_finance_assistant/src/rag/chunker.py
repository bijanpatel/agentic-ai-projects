import json
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def load_kb_documents(file_path: str) -> list[Document]:
    documents = []
    path = Path(file_path)

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line.strip())
            doc = Document(
                page_content=record["content"],
                metadata={
                    "doc_id": record["doc_id"],
                    "title": record["title"],
                    "category": record["category"],
                    "source": record["source"],
                    "difficulty": record["difficulty"],
                    "tags": ", ".join(record["tags"]),
                },
            )
            documents.append(doc)

    return documents


def chunk_documents(documents: list[Document], chunk_size: int = 700, chunk_overlap: int = 100) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_documents(documents)