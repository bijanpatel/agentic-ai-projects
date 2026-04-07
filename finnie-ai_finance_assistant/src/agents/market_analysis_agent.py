from langchain_openai import ChatOpenAI
from src.core.config import load_config
from src.utils.market_data import get_ticker_snapshot


MARKET_ANALYSIS_SYSTEM_PROMPT = """
You are a beginner-friendly market analysis assistant.

Your role:
- Explain live market data in simple language.
- Keep responses short, clear, and educational.
- Focus on helping the user understand what the numbers mean.

Important rules:
- Do NOT provide personalized investment advice.
- Do NOT tell the user to buy, sell, or hold a security.
- If data is missing, say so clearly.
"""


def ask_market_question(user_query: str, ticker: str) -> dict:
    """
    Answer a market-related question using live data from yfinance.

    Parameters:
        user_query (str):
            The user's market question.
            Example: "What is Apple stock price today?"

        ticker (str):
            Ticker symbol to analyze.
            Example: "AAPL"

    Returns:
        dict:
            Structured response containing:
            - question
            - answer
            - market_data
            - agent
    """
    config = load_config()
    snapshot = get_ticker_snapshot(ticker)

    if not snapshot.get("current_price"):
        return {
            "question": user_query,
            "answer": f"I could not retrieve live market data for {ticker} right now.",
            "market_data": snapshot,
            "agent": "market_analysis"
        }

    llm = ChatOpenAI(
        api_key=config["openai_api_key"],
        model=config["model_name"],
        temperature=config["model"]["temperature"]
    )

    user_prompt = f"""
User question:
{user_query}

Live market data:
{snapshot}

Explain this in a simple, educational way for a beginner.
"""

    response = llm.invoke([
        {"role": "system", "content": MARKET_ANALYSIS_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ])

    return {
        "question": user_query,
        "answer": response.content,
        "market_data": snapshot,
        "agent": "market_analysis"
    }