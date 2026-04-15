from src.agents.ticker_extractor_agent import extract_ticker_hybrid


def detect_handoff_need(user_query: str, routed_agent: str) -> str | None:
    """
    Decide whether the workflow should hand off from the primary agent
    to a secondary agent.
    """
    q = user_query.lower().strip()

    # Handoff 1: News -> Market
    # Only hand off if the news query includes a real ticker/company signal.
    if routed_agent == "news_synthesizer":
        ticker = extract_ticker_hybrid(user_query, default_ticker=None)
        if ticker:
            return "market_analysis"

    # Handoff 2: Portfolio -> Finance Q&A
    if routed_agent == "portfolio_analysis":
        if any(word in q for word in [
            "what does that mean",
            "explain diversification",
            "what is diversification",
            "concentration risk",
            "asset allocation",
        ]):
            return "finance_qa"

    # Handoff 3: Goal Planning -> Tax Education
    if routed_agent == "goal_planning":
        if any(word in q for word in [
            "roth ira", "401k", "401(k)", "ira", "tax", "retirement account"
        ]):
            return "tax_education"

    return None