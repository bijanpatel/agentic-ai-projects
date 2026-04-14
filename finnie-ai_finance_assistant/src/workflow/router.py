import re
from src.agents.router_agent import llm_route_query


def looks_like_ticker(text: str) -> bool:
    """
    Very simple ticker-pattern check.

    Parameters:
        text (str):
            User query text.

    Returns:
        bool:
            True if the query appears to contain a ticker-like symbol.
    """
    pattern = r"\b[A-Z]{1,5}\b"
    return bool(re.search(pattern, text))


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

    market_keywords = [
        "stock price", "price today", "trading at", "market data", "ticker",
        "current price", "price of", "what is happening with"
    ]

    if any(keyword in q for keyword in tax_keywords):
        return "tax_education"

    if any(keyword in q for keyword in goal_keywords):
        return "goal_planning"

    if any(keyword in q for keyword in news_keywords):
        return "news_synthesizer"

    if any(keyword in q for keyword in portfolio_keywords):
        return "portfolio_analysis"

    if any(keyword in q for keyword in market_keywords) or looks_like_ticker(user_query):
        return "market_analysis"

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