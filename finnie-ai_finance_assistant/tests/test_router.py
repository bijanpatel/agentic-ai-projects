import json
from pathlib import Path
from src.workflow.router import route_query


SUPPORTED_ROUTES = {
    "finance_qa",
    "tax_education",
    "goal_planning",
}


def test_routing_eval_set_for_current_supported_routes():
    """
    Validate that the rule-based router sends currently supported
    workflow queries to the expected agent.

    Current workflow-supported routes:
    - finance_qa
    - tax_education
    - goal_planning

    Why this filtering exists:
        The evaluation dataset includes future routes such as
        portfolio_analysis, market_analysis, and news_synthesizer,
        but those are not yet part of the current LangGraph chat workflow.
    """
    path = Path("src/data/eval/routing_eval_set.json")

    with path.open("r", encoding="utf-8") as f:
        cases = json.load(f)

    filtered_cases = [
        case for case in cases
        if case["expected_route"] in SUPPORTED_ROUTES
    ]

    for case in filtered_cases:
        user_input = case["input"]
        expected_route = case["expected_route"]

        actual_route = route_query(user_input)

        assert actual_route == expected_route, (
            f"Query '{user_input}' routed to '{actual_route}' "
            f"instead of expected '{expected_route}'"
        )