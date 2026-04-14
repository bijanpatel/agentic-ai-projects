def detect_handoff_need(user_query: str, routed_agent: str) -> str | None:
    """
    Decide whether the workflow should hand off from the primary agent
    to a secondary agent.

    Parameters:
        user_query (str):
            The original user query.

        routed_agent (str):
            The primary agent selected by the router.

    Returns:
        str | None:
            The secondary agent name if a handoff is needed, otherwise None.

    Implemented handoff rules:
        - news_synthesizer -> market_analysis
        - portfolio_analysis -> finance_qa
        - goal_planning -> tax_education

    Why this file exists:
        It separates handoff logic from the main router logic so the design
        stays cleaner and easier to expand.
    """
    q = user_query.lower().strip()

    # Handoff 1: News -> Market
    if routed_agent == "news_synthesizer":
        if any(word in q for word in ["aapl", "msft", "nvda", "tsla", "voo", "ticker", "stock", "shares"]):
            return "market_analysis"

    # Handoff 2: Portfolio -> Finance Q&A
    if routed_agent == "portfolio_analysis":
        if any(word in q for word in ["what does that mean", "explain diversification", "what is diversification", "concentration risk", "asset allocation"]):
            return "finance_qa"

    # Handoff 3: Goal Planning -> Tax Education
    if routed_agent == "goal_planning":
        if any(word in q for word in ["roth ira", "401k", "401(k)", "ira", "tax", "retirement account"]):
            return "tax_education"

    return None