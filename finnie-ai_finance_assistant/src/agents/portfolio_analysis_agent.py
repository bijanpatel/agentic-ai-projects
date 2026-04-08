import json
from langchain_openai import ChatOpenAI

from src.core.config import load_config
from src.tools.finance_tools import calculate_portfolio_metrics_tool
from src.rag.retriever import search_documents


PORTFOLIO_ANALYSIS_SYSTEM_PROMPT = """
You are a beginner-friendly portfolio analysis assistant.

Your role:
- Explain portfolio composition clearly and simply.
- Help the user understand diversification, concentration, and asset mix.
- Use the provided portfolio metrics as the main source of truth.
- Use retrieved educational context when relevant.

Important rules:
- Do NOT provide personalized investment advice.
- Do NOT recommend buying or selling securities.
- Keep the response educational and easy to understand.
"""


def format_context(docs) -> str:
    """
    Convert retrieved educational documents into a prompt-ready text block.

    Parameters:
        docs (list):
            Retrieved document objects.

    Returns:
        str:
            Formatted text context.
    """
    if not docs:
        return "No relevant educational context was retrieved."

    parts = []
    for i, doc in enumerate(docs, start=1):
        parts.append(
            f"[Document {i}]\n"
            f"Title: {doc.metadata.get('title', 'Untitled')}\n"
            f"Category: {doc.metadata.get('category', 'unknown')}\n"
            f"Source: {doc.metadata.get('source', 'unknown')}\n"
            f"Content: {doc.page_content}\n"
        )
    return "\n".join(parts)


def extract_sources(docs) -> list[dict]:
    """
    Extract unique source references from retrieved documents.
    """
    seen = set()
    sources = []

    for doc in docs:
        title = doc.metadata.get("title", "Untitled")
        source = doc.metadata.get("source", "unknown")
        key = (title, source)

        if key not in seen:
            seen.add(key)
            sources.append({"title": title, "source": source})

    return sources


def ask_portfolio_question(user_query: str, portfolio_id: str) -> dict:
    """
    Analyze a sample portfolio using a tool-based metrics call plus optional
    RAG grounding for educational concepts.

    Parameters:
        user_query (str):
            Portfolio-related user question.

        portfolio_id (str):
            Portfolio identifier such as "p1".

    Returns:
        dict:
            Structured response containing:
            - question
            - answer
            - portfolio_metrics
            - sources
            - agent
            - used_rag
            - used_api
            - fallback_used
    """
    config = load_config()

    metrics_json = calculate_portfolio_metrics_tool.invoke({"portfolio_id": portfolio_id})
    metrics = json.loads(metrics_json)

    # Retrieve educational support docs for better grounding.
    docs = search_documents(
        "diversification asset allocation concentration risk portfolio",
        k=config["rag"]["top_k"]
    )
    context = format_context(docs)
    sources = extract_sources(docs)

    llm = ChatOpenAI(
        api_key=config["openai_api_key"],
        model=config["model_name"],
        temperature=config["model"]["temperature"]
    )

    user_prompt = f"""
User question:
{user_query}

Portfolio metrics:
{json.dumps(metrics, indent=2)}

Educational context:
{context}

Explain the portfolio in a simple, educational way for a beginner.

Please highlight:
- total value
- diversification observations
- concentration observations
- asset type mix
- any educational risk considerations
"""

    response = llm.invoke([
        {"role": "system", "content": PORTFOLIO_ANALYSIS_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ])

    return {
        "question": user_query,
        "answer": response.content,
        "portfolio_metrics": metrics,
        "sources": sources,
        "agent": "portfolio_analysis",
        "used_rag": True,
        "used_api": False,
        "fallback_used": False,
    }