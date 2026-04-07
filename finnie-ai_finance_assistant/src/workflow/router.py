def route_query(user_query: str) -> str:
    """
    Route the user query to the appropriate agent.

    Parameters:
        user_query (str):
            The raw question asked by the user.

    Returns:
        str:
            The name of the selected agent.

    Routing logic:
        - tax_education:
            For tax-related terms such as Roth IRA, 401(k), capital gains, taxable account.
        - goal_planning:
            For goal-oriented terms such as emergency fund, save, house, retirement, time horizon.
        - finance_qa:
            Default route for general finance education questions.

    Notes:
        This is a simple rule-based router for the MVP.
        Later, we can replace or enhance it with an LLM-based intent classifier.
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

    if any(keyword in q for keyword in tax_keywords):
        return "tax_education"

    if any(keyword in q for keyword in goal_keywords):
        return "goal_planning"

    return "finance_qa"