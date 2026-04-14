import re


def parse_simple_holdings(user_query: str) -> list[dict]:
    """
    Parse a simple holdings format from user text.

    Expected format examples:
        'AAPL 10, VOO 5, BND 7'
        'MSFT 12 NVDA 4'

    Parameters:
        user_query (str):
            Raw user message.

    Returns:
        list[dict]:
            Parsed holdings in the form:
            [
              {"ticker": "AAPL", "quantity": 10},
              {"ticker": "VOO", "quantity": 5}
            ]
    """
    pattern = r"\b([A-Za-z]{1,5})\s+(\d+)\b"
    matches = re.findall(pattern, user_query)

    holdings = []
    for ticker, quantity in matches:
        holdings.append({
            "ticker": ticker.upper(),
            "quantity": int(quantity),
        })

    return holdings


def handle_portfolio_intake(user_query: str, portfolio_context: dict | None = None) -> dict:
    """
    Handle conversational portfolio intake.

    Parameters:
        user_query (str):
            Current user message.

        portfolio_context (dict | None):
            Existing portfolio context in state, if any.

    Returns:
        dict:
            Structured result indicating whether follow-up is needed
            or whether holdings were successfully captured.
    """
    portfolio_context = portfolio_context or {}

    holdings = parse_simple_holdings(user_query)

    if not holdings:
        return {
            "question": user_query,
            "answer": (
                "I can help analyze your portfolio. "
                "Please share your holdings in a simple format like: "
                "AAPL 10, VOO 5, BND 7"
            ),
            "agent": "portfolio_intake",
            "used_rag": False,
            "used_api": False,
            "fallback_used": False,
            "handoff_used": False,
            "needs_followup": True,
            "followup_type": "portfolio_holdings",
            "portfolio_context": portfolio_context,
        }

    portfolio_context["holdings"] = holdings

    return {
        "question": user_query,
        "answer": "Got it — I captured your holdings and can now analyze the portfolio.",
        "agent": "portfolio_intake",
        "used_rag": False,
        "used_api": False,
        "fallback_used": False,
        "handoff_used": False,
        "needs_followup": False,
        "followup_type": "",
        "portfolio_context": portfolio_context,
    }