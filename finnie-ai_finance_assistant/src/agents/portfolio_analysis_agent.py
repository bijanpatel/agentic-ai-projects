import json
from langchain_openai import ChatOpenAI

from src.core.config import load_config
from src.tools.finance_tools import calculate_portfolio_metrics_tool
from src.rag.retriever import search_documents
from src.agents.market_analysis_agent import ask_market_question


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
    Analyze a sample portfolio using a tool-based metrics call plus educational RAG grounding.
    """
    config = load_config()

    metrics_json = calculate_portfolio_metrics_tool.invoke({"portfolio_id": portfolio_id})
    metrics = json.loads(metrics_json)

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
- educational risk considerations
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
def analyze_chat_holdings_portfolio(holdings: list[dict], user_query: str) -> dict:
    """
    Analyze holdings captured directly from chat input.

    Parameters:
        holdings (list[dict]):
            Example:
            [
                {"ticker": "AAPL", "quantity": 10},
                {"ticker": "VOO", "quantity": 5}
            ]

        user_query (str):
            Original user query.

    Returns:
        dict:
            Beginner-friendly portfolio analysis result.
    """
    enriched_holdings = []
    total_value = 0.0

    for holding in holdings:
        ticker = holding["ticker"]
        quantity = float(holding["quantity"])

        market_result = ask_market_question(
            user_query=f"What is happening with {ticker} right now?",
            ticker=ticker
        )

        market_data = market_result.get("market_data", {})
        current_price = market_data.get("current_price", 0.0) or 0.0
        holding_value = float(current_price) * quantity

        enriched_holdings.append({
            "ticker": ticker,
            "quantity": quantity,
            "current_price": float(current_price),
            "holding_value": holding_value,
            "sector": market_data.get("sector", "Unknown"),
            "asset_type": market_data.get("asset_type", "Unknown"),
        })

        total_value += holding_value

    for h in enriched_holdings:
        h["allocation_pct"] = (h["holding_value"] / total_value * 100) if total_value > 0 else 0.0

    sector_totals = {}
    for h in enriched_holdings:
        sector = h.get("sector", "Unknown")
        sector_totals[sector] = sector_totals.get(sector, 0.0) + h["holding_value"]

    sector_allocation = [
        {"sector": sector, "value": value}
        for sector, value in sector_totals.items()
    ]

    answer = (
        f"I analyzed your portfolio with {len(enriched_holdings)} holdings. "
        f"The estimated total value is ${total_value:,.2f}. "
        f"Use the allocation breakdown to check diversification and concentration risk."
    )

    return {
    "question": user_query,
    "answer": answer,
    "portfolio_metrics": {
        "total_value": total_value,
        "total_cost_basis": 0.0,
        "unrealized_gain_loss": 0.0,
        "holdings": enriched_holdings,
        "sector_allocation": sector_allocation,
    },
    "sources": [],
    "agent": "portfolio_analysis",
    "used_rag": False,
    "used_api": True,
    "fallback_used": False,
}