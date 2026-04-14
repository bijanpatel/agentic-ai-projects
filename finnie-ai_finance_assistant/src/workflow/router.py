import re
from src.agents.router_agent import llm_route_query


def looks_like_ticker(text: str) -> bool:
    """
    Check whether the query contains a likely stock/ETF ticker symbol.

    Rules:
    - 2 to 5 uppercase alphabetic characters
    - reject common greetings and common English short words
    - this only detects ticker-like tokens, not market intent by itself
    """
    blocked_words = {
        "HI", "HEY", "HELLO", "WHO", "WHAT", "WITH", "NEWS", "ABOUT",
        "TODAY", "PRICE", "HOW", "ARE", "YOU", "THE", "AND", "FOR",
        "THIS", "THAT", "GOOD", "MORNING", "EVENING", "AFTERNOON"
    }

    tokens = text.upper().split()

    for token in tokens:
        cleaned = token.strip(",.?!:;()[]{}\"'")
        if 2 <= len(cleaned) <= 5 and cleaned.isalpha():
            if cleaned not in blocked_words:
                return True

    return False


def has_clear_market_intent(user_query: str) -> bool:
    """
    Check whether the query clearly asks for market/ticker-related information.

    Parameters:
        user_query (str):
            Raw user query.

    Returns:
        bool:
            True if the query clearly sounds market-related.
    """
    q = user_query.lower().strip()

    market_keywords = [
        "stock price",
        "price today",
        "trading at",
        "market data",
        "ticker",
        "current price",
        "price of",
        "what is happening with",
        "how is",
        "how's",
        "share price",
        "stock doing",
        "market performance",
        "latest price",
    ]

    return any(keyword in q for keyword in market_keywords)


def rule_based_route(user_query: str) -> str | None:
    """
    Try rule-based routing first.

    Parameters:
        user_query (str):
            Raw user query.

    Returns:
        str | None:
            Agent name if a strong rule match is found, otherwise None.

    Why return None?
        None means the query was ambiguous and should be handed to the LLM router.
    """
    q = user_query.lower().strip()

    tax_keywords = [
        "roth ira", "401(k)", "401k", "capital gains", "tax", "taxable",
        "tax-advantaged", "ira", "retirement account"
    ]

    goal_keywords = [
        "save", "saving", "goal", "emergency fund", "house", "down payment",
        "retirement", "time horizon", "monthly contribution", "risk tolerance"
    ]

    news_keywords = [
        "news", "headline", "headlines", "summarize news", "market news",
        "what happened today", "market update", "latest market news", "recent market news"
    ]

    portfolio_keywords = [
        "portfolio", "holdings", "allocation", "diversified", "diversification",
        "concentration", "analyze my portfolio"
    ]

    # Strong deterministic routes first
    if any(keyword in q for keyword in tax_keywords):
        return "tax_education"

    if any(keyword in q for keyword in goal_keywords):
        return "goal_planning"

    if any(keyword in q for keyword in news_keywords):
        return "news_synthesizer"

    if any(keyword in q for keyword in portfolio_keywords):
        return "portfolio_analysis"

    # Route to market only when the query clearly sounds market-related.
    if has_clear_market_intent(user_query):
        return "market_analysis"

    # Ticker-like token alone is NOT enough anymore.
    # Let ambiguous cases go to the LLM router instead.
    if looks_like_ticker(user_query):
        return None

    # No strong rule match found.
    return None


def route_query(user_query: str) -> str:
    """
    Hybrid router:
    1. Try rule-based routing
    2. If no strong match, use the LLM Router Agent

    Parameters:
        user_query (str):
            User question.

    Returns:
        str:
            Selected agent name.
    """
    rule_result = rule_based_route(user_query)

    if rule_result is not None:
        return rule_result

    return llm_route_query(user_query)