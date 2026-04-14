def route_query(user_query: str) -> str:
    """
    Route the user query to the appropriate agent.

    Parameters:
        user_query (str):
            The raw question asked by the user.

    Returns:
        str:
            The name of the selected agent.

    Current supported routes:
        - finance_qa
        - tax_education
        - goal_planning
        - news_synthesizer

    Notes:
        This is still a rule-based router for the MVP.
        It can be upgraded later into a model-based router.
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
        "what happened today", "today in markets", "what's happening in the market",
        "what is happening in the market", "market update", "latest market news",
        "recent market news", "summarize recent market news"
    ]

    if any(keyword in q for keyword in tax_keywords):
        return "tax_education"

    if any(keyword in q for keyword in goal_keywords):
        return "goal_planning"

    if any(keyword in q for keyword in news_keywords):
        return "news_synthesizer"

    return "finance_qa"