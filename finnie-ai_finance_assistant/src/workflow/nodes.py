from src.agents.finance_qa_agent import ask_finance_question
from src.agents.tax_education_agent import ask_tax_question
from src.agents.goal_planning_agent import ask_goal_question
from src.agents.news_synthesizer_agent import ask_news_question
from src.agents.market_analysis_agent import ask_market_question
from src.agents.portfolio_analysis_agent import ask_portfolio_question
from src.workflow.router import route_query
from src.workflow.handoff import detect_handoff_need


def extract_ticker_from_query(user_query: str) -> str:
    """
    Very simple ticker extraction for market queries.

    Parameters:
        user_query (str):
            Raw user query.

    Returns:
        str:
            Extracted ticker symbol if found, otherwise 'AAPL'.

    Why default to AAPL?
        Keeps the demo flow resilient while we build a more robust parser later.
    """
    tokens = user_query.upper().split()

    for token in tokens:
        cleaned = token.strip(",.?!")
        if 1 <= len(cleaned) <= 5 and cleaned.isalpha():
            if cleaned not in {"WHAT", "WITH", "PRICE", "TODAY", "MARKET", "NEWS"}:
                return cleaned

    return "AAPL"

def router_node(state: dict) -> dict:
    """
    Router node for the workflow.
    """
    user_query = state["user_query"]
    state["routed_agent"] = route_query(user_query)
    state["handoff_to"] = None
    state["primary_result"] = None
    return state

def finance_qa_node(state: dict) -> dict:
    """
    Finance Q&A node.
    """
    result = ask_finance_question(state["user_query"])
    state["result"] = result
    state["primary_result"] = result
    state["handoff_to"] = detect_handoff_need(state["user_query"], "finance_qa")
    return state


def goal_planning_node(state: dict) -> dict:
    """
    Goal Planning node.
    """
    result = ask_goal_question(state["user_query"])
    state["result"] = result
    state["primary_result"] = result
    state["handoff_to"] = detect_handoff_need(state["user_query"], "goal_planning")
    return state

def tax_education_node(state: dict) -> dict:
    """
    Tax Education node.
    """
    result = ask_tax_question(state["user_query"])
    state["result"] = result
    state["primary_result"] = result
    state["handoff_to"] = detect_handoff_need(state["user_query"], "tax_education")
    return state


def news_synthesizer_node(state: dict) -> dict:
    """
    News Synthesizer node.
    """
    result = ask_news_question(state["user_query"])
    state["result"] = result
    state["primary_result"] = result
    state["handoff_to"] = detect_handoff_need(state["user_query"], "news_synthesizer")
    return state

def market_analysis_node(state: dict) -> dict:
    """
    Market Analysis node.
    """
    ticker = extract_ticker_from_query(state["user_query"])
    result = ask_market_question(state["user_query"], ticker=ticker)
    state["result"] = result
    return state

def portfolio_analysis_node(state: dict) -> dict:
    """
    Portfolio Analysis node.
    """
    result = ask_portfolio_question(
        user_query=state["user_query"],
        portfolio_id="p1"
    )
    state["result"] = result
    state["primary_result"] = result
    state["handoff_to"] = detect_handoff_need(state["user_query"], "portfolio_analysis")
    return state

def merge_results_node(state: dict) -> dict:
    """
    Merge primary and secondary agent outputs into a single final response.

    Parameters:
        state (dict):
            Shared workflow state containing:
            - primary_result
            - result (secondary result after handoff)

    Returns:
        dict:
            Updated state with merged result.

    Why this node matters:
        It gives the user one coherent answer even when two agents contributed.
    """
    primary = state.get("primary_result")
    secondary = state.get("result")

    if not primary or not secondary:
        return state

    merged_answer = (
        f"{primary.get('answer', '')}\n\n"
        f"Additional perspective from {secondary.get('agent', 'secondary agent')}:\n"
        f"{secondary.get('answer', '')}"
    )

    merged_sources = []
    merged_sources.extend(primary.get("sources", []))
    merged_sources.extend(secondary.get("sources", []))

    # Deduplicate sources.
    unique_sources = []
    seen = set()
    for source in merged_sources:
        key = (source.get("title"), source.get("source"))
        if key not in seen:
            seen.add(key)
            unique_sources.append(source)

    state["result"] = {
        "question": state.get("user_query"),
        "answer": merged_answer,
        "sources": unique_sources,
        "agent": f"{primary.get('agent')} -> {secondary.get('agent')}",
        "used_rag": primary.get("used_rag", False) or secondary.get("used_rag", False),
        "used_api": primary.get("used_api", False) or secondary.get("used_api", False),
        "fallback_used": primary.get("fallback_used", False) or secondary.get("fallback_used", False),
        "handoff_used": True,
        "primary_agent": primary.get("agent"),
        "secondary_agent": secondary.get("agent"),
    }

    return state

def news_to_market_node(state: dict) -> dict:
    """
    Handoff node: after news synthesis, add market analysis context.
    """
    primary = state.get("primary_result")
    ticker = extract_ticker_from_query(state["user_query"])
    secondary = ask_market_question(state["user_query"], ticker=ticker)

    merged_answer = (
        f"{primary.get('answer', '')}\n\n"
        f"Additional market context:\n{secondary.get('answer', '')}"
    )

    merged_sources = []
    merged_sources.extend(primary.get("sources", []))
    merged_sources.extend(secondary.get("sources", []))

    unique_sources = []
    seen = set()
    for source in merged_sources:
        key = (source.get("title"), source.get("source"))
        if key not in seen:
            seen.add(key)
            unique_sources.append(source)

    state["result"] = {
        "question": state["user_query"],
        "answer": merged_answer,
        "sources": unique_sources,
        "agent": "news_synthesizer -> market_analysis",
        "used_rag": primary.get("used_rag", False) or secondary.get("used_rag", False),
        "used_api": primary.get("used_api", False) or secondary.get("used_api", False),
        "fallback_used": primary.get("fallback_used", False) or secondary.get("fallback_used", False),
        "handoff_used": True,
        "primary_agent": "news_synthesizer",
        "secondary_agent": "market_analysis",
    }
    return state


def portfolio_to_finance_node(state: dict) -> dict:
    """
    Handoff node: after portfolio analysis, add finance concept explanation.
    """
    primary = state.get("primary_result")
    secondary = ask_finance_question("Explain diversification and concentration risk in simple terms.")

    merged_answer = (
        f"{primary.get('answer', '')}\n\n"
        f"Additional finance explanation:\n{secondary.get('answer', '')}"
    )

    merged_sources = []
    merged_sources.extend(primary.get("sources", []))
    merged_sources.extend(secondary.get("sources", []))

    unique_sources = []
    seen = set()
    for source in merged_sources:
        key = (source.get("title"), source.get("source"))
        if key not in seen:
            seen.add(key)
            unique_sources.append(source)

    state["result"] = {
        "question": state["user_query"],
        "answer": merged_answer,
        "sources": unique_sources,
        "agent": "portfolio_analysis -> finance_qa",
        "used_rag": primary.get("used_rag", False) or secondary.get("used_rag", False),
        "used_api": primary.get("used_api", False) or secondary.get("used_api", False),
        "fallback_used": primary.get("fallback_used", False) or secondary.get("fallback_used", False),
        "handoff_used": True,
        "primary_agent": "portfolio_analysis",
        "secondary_agent": "finance_qa",
    }
    return state


def goal_to_tax_node(state: dict) -> dict:
    """
    Handoff node: after goal planning, add tax account education.
    """
    primary = state.get("primary_result")
    secondary = ask_tax_question("Explain Roth IRA versus 401(k) in simple terms.")

    merged_answer = (
        f"{primary.get('answer', '')}\n\n"
        f"Additional tax account explanation:\n{secondary.get('answer', '')}"
    )

    merged_sources = []
    merged_sources.extend(primary.get("sources", []))
    merged_sources.extend(secondary.get("sources", []))

    unique_sources = []
    seen = set()
    for source in merged_sources:
        key = (source.get("title"), source.get("source"))
        if key not in seen:
            seen.add(key)
            unique_sources.append(source)

    state["result"] = {
        "question": state["user_query"],
        "answer": merged_answer,
        "sources": unique_sources,
        "agent": "goal_planning -> tax_education",
        "used_rag": primary.get("used_rag", False) or secondary.get("used_rag", False),
        "used_api": primary.get("used_api", False) or secondary.get("used_api", False),
        "fallback_used": primary.get("fallback_used", False) or secondary.get("fallback_used", False),
        "handoff_used": True,
        "primary_agent": "goal_planning",
        "secondary_agent": "tax_education",
    }
    return state