from src.rag.retriever import search_documents


def test_rag_returns_docs_for_etf_query():
    """
    Test that a known in-domain finance query returns at least one document.
    """
    docs = search_documents("What is an ETF?", k=4, score_threshold=0.5)
    assert len(docs) > 0, "Expected at least one document for ETF query"


def test_rag_returns_etf_related_doc_for_etf_query():
    """
    Test that an ETF query retrieves at least one clearly relevant ETF/fund-related document.
    """
    docs = search_documents("What is an ETF?", k=4, score_threshold=0.5)

    titles = [doc.metadata.get("title", "").lower() for doc in docs]

    assert any(
        "etf" in title or "index investing" in title or "broad market funds" in title
        for title in titles
    ), f"Expected an ETF-related document, got titles: {titles}"