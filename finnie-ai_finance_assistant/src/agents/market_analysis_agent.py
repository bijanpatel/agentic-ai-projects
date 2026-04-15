import json
from langchain_openai import ChatOpenAI

from src.core.config import load_config
from src.tools.finance_tools import get_market_snapshot_tool, get_price_history_tool


MARKET_ANALYSIS_SYSTEM_PROMPT = """
You are a beginner-friendly market analysis assistant.

Your role:
- Explain market data in simple language.
- Use tool results as the source of truth.
- Help the user understand what the numbers mean.

Important rules:
- Do NOT provide personalized investment advice.
- Do NOT tell the user to buy, sell, or hold a security.
- If data is missing, say so clearly.
- Keep the explanation concise and educational.
"""


def ask_market_question(user_query: str, ticker: str) -> dict:
    """
    Answer a market-related question using tool-based market data access.

    Parameters:
        user_query (str):
            The user's market question.

        ticker (str):
            Ticker symbol to analyze.

    Returns:
        dict:
            Structured response containing:
            - question
            - answer
            - market_data
            - recent_history_rows
            - agent
            - used_rag
            - used_api
            - fallback_used
    """
    config = load_config()

    if not ticker:
        return {
            "question": user_query,
            "answer": "I can help with market analysis, but I need a specific stock or ETF ticker such as AAPL, MSFT, or VOO.",
            "market_data": {},
            "sources": [],
            "agent": "market_analysis",
            "used_rag": False,
            "used_api": False,
            "fallback_used": True,
        }

    snapshot_json = get_market_snapshot_tool.invoke({"ticker": ticker})
    history_json = get_price_history_tool.invoke({
        "ticker": ticker,
        "period": "1mo",
        "interval": "1d"
    })

    snapshot = json.loads(snapshot_json)
    history = json.loads(history_json)

    if not snapshot.get("current_price"):
        return {
            "question": user_query,
            "answer": f"I could not retrieve live market data for {ticker} right now.",
            "market_data": snapshot,
            "recent_history_rows": len(history) if isinstance(history, list) else 0,
            "agent": "market_analysis",
            "used_rag": False,
            "used_api": True,
            "fallback_used": True,
        }

    llm = ChatOpenAI(
        api_key=config["openai_api_key"],
        model=config["model_name"],
        temperature=config["model"]["temperature"]
    )

    user_prompt = f"""
User question:
{user_query}

Live market snapshot:
{json.dumps(snapshot, indent=2)}

Recent price history:
{json.dumps(history[:10], indent=2) if isinstance(history, list) else history}

Explain this in a simple, educational way for a beginner.
Mention what stands out from the current price and recent trend.
"""

    response = llm.invoke([
        {"role": "system", "content": MARKET_ANALYSIS_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ])

    return {
        "question": user_query,
        "answer": response.content,
        "market_data": snapshot,
        "recent_history_rows": len(history) if isinstance(history, list) else 0,
        "agent": "market_analysis",
        "used_rag": False,
        "used_api": True,
        "fallback_used": False,
    }