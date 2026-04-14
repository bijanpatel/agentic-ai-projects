import re


def looks_like_ticker(text: str) -> bool:
    """
    Very simple ticker-pattern check.

    Parameters:
        text (str):
            User query in lowercase or original form.

    Returns:
        bool:
            True if the text appears to contain a ticker-like token.

    Note:
        This is intentionally simple for MVP use.
        Later this can be upgraded with a stronger parser.
    """
    pattern = r"\b[A-Z]{1,5}\b"
    return bool(re.search(pattern, text))


def route_query(user_query: str) -> str:
    """
    Route the user query to the appropriate agent.

    Parameters:
        user_query (str):
            The raw question asked by the user.

    Returns:
        str:
            The name of the selected agent.

    Supported routes:
        - finance_qa
        - tax_education
        - goal_planning
        - news_synthesizer
        - market_analysis
        - portfolio_analysis

    Why this router matters:
        It allows the user to use one main chat interface while the system
        decides which specialized agent should respond.
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
        "what happened today", "today in markets", "market update",
        "latest market news", "recent market news"
    ]

    portfolio_keywords = [
        "portfolio", "holdings", "allocation", "diversified", "diversification",
        "concentration", "my investments", "analyze my portfolio"
    ]

    market_keywords = [
        "stock price", "price today", "trading at", "market data", "ticker",
        "what is happening with", "how is", "current price", "price of"
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

    return "finance_qa"