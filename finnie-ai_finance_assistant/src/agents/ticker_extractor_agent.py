import json
import re
from pathlib import Path

from langchain_openai import ChatOpenAI
from src.core.config import load_config


TICKER_EXTRACTION_SYSTEM_PROMPT = """
You are a financial ticker extraction assistant.

Your job:
- Read the user's query
- Identify the most likely stock or ETF ticker if one is mentioned directly or indirectly
- Return only valid JSON

Output format:
{
  "ticker": "<TICKER_OR_EMPTY_STRING>"
}

Rules:
- If the query clearly refers to a company like Apple, return its stock ticker if you know it confidently
- If the query clearly refers to a well-known ETF like VOO, return that ticker
- If no ticker can be identified confidently, return an empty string
- Do not include any explanation
- Return only JSON
"""


def load_ticker_aliases(file_path: str = "src/data/mappings/ticker_aliases.json") -> dict:
    """
    Load known aliases and company-name to ticker mappings.

    Parameters:
        file_path (str):
            Path to the ticker alias mapping JSON file.

    Returns:
        dict:
            Dictionary mapping lowercased aliases to ticker strings.
    """
    path = Path(file_path)

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def extract_ticker_from_alias_map(user_query: str) -> str | None:
    """
    Try to identify a ticker using a local alias dictionary.

    Parameters:
        user_query (str):
            Raw user query.

    Returns:
        str | None:
            Matched ticker if found, otherwise None.

    Why this step exists:
        It is deterministic, cheap, and handles common company names reliably.
    """
    aliases = load_ticker_aliases()
    q = user_query.lower()

    # Sort longer keys first so "s&p 500 etf" matches before "s&p 500"
    for alias in sorted(aliases.keys(), key=len, reverse=True):
        if alias in q:
            return aliases[alias]

    return None


def looks_like_valid_ticker(ticker: str) -> bool:
    """
    Basic validation for ticker-like strings.

    Parameters:
        ticker (str):
            Candidate ticker.

    Returns:
        bool:
            True if the ticker looks valid for our MVP use.
    """
    if not ticker:
        return False

    blocked_words = {
        "ABOUT", "WHAT", "WITH", "PRICE", "TODAY", "MARKET",
        "NEWS", "FOR", "THE", "AND", "THIS", "THAT"
    }

    if ticker in blocked_words:
        return False

    return bool(re.fullmatch(r"[A-Z]{1,5}", ticker))


def extract_ticker_with_llm(user_query: str) -> str | None:
    """
    Use the LLM to extract a likely ticker from the user query.

    Parameters:
        user_query (str):
            Raw user query.

    Returns:
        str | None:
            Extracted ticker if valid, otherwise None.

    Why this step exists:
        It helps when the user uses natural language or company names not covered
        by the alias dictionary.
    """
    config = load_config()

    llm = ChatOpenAI(
        api_key=config["openai_api_key"],
        model=config["model_name"],
        temperature=0.0,
    )

    response = llm.invoke([
        {"role": "system", "content": TICKER_EXTRACTION_SYSTEM_PROMPT},
        {"role": "user", "content": f"User query:\n{user_query}"}
    ])

    try:
        parsed = json.loads(response.content)
        ticker = parsed.get("ticker", "").strip().upper()
        if looks_like_valid_ticker(ticker):
            return ticker
    except (json.JSONDecodeError, TypeError, ValueError):
        return None

    return None


def extract_ticker_hybrid(user_query: str, default_ticker: str = "AAPL") -> str:
    """
    Hybrid ticker extraction strategy.

    Steps:
        1. Try alias/dictionary lookup
        2. Try LLM-based extraction
        3. Fall back to default ticker

    Parameters:
        user_query (str):
            Raw user query.

        default_ticker (str):
            Safe fallback ticker for demo resilience.

    Returns:
        str:
            Final ticker symbol to use.

    Why this function matters:
        It gives us a stronger extraction strategy than manual string scanning
        while still staying simple enough for the project timeline.
    """
    alias_ticker = extract_ticker_from_alias_map(user_query)
    if alias_ticker and looks_like_valid_ticker(alias_ticker):
        return alias_ticker

    llm_ticker = extract_ticker_with_llm(user_query)
    if llm_ticker and looks_like_valid_ticker(llm_ticker):
        return llm_ticker

    return default_ticker