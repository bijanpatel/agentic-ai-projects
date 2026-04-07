from src.rag.vector_store import get_vector_store


def get_retriever(k: int = 4, score_threshold: float = 0.5):
    """
    Create a retriever from the Chroma vector store.

    Parameters:
        k (int):
            Maximum number of documents to retrieve.
            If k=4, the retriever will return up to 4 matching documents.

        score_threshold (float):
            Minimum similarity score required for a document to be included.
            This helps filter out weak or unrelated matches.

            Why this matters:
            - Without a threshold, the retriever may always return documents,
              even when they are not truly relevant.
            - With a threshold, unrelated queries can correctly return 0 documents.

            Tuning guide:
            - 0.7 = stricter matching, fewer results
            - 0.5 = more flexible, often better for small knowledge bases

    Returns:
        Retriever:
            A LangChain retriever object that can be used to search documents.
    """
    vector_store = get_vector_store()

    return vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": k,
            "score_threshold": score_threshold
        }
    )


def search_documents(query: str, k: int = 4, score_threshold: float = 0.5):
    """
    Search the knowledge base for documents relevant to the user's query.

    Parameters:
        query (str):
            The user question to search for.
            Example: "What is an ETF?"

        k (int):
            Maximum number of documents to return.

        score_threshold (float):
            Minimum relevance score required for documents to be returned.

    Returns:
        list:
            A list of retrieved document objects.
    """
    retriever = get_retriever(k=k, score_threshold=score_threshold)
    docs = retriever.invoke(query)
    return docs