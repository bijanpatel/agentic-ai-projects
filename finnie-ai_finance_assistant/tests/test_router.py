import json
from pathlib import Path
from src.workflow.router import rule_based_route


SUPPORTED_RULE_ROUTES = {
    "finance_qa",
    "tax_education",
    "goal_planning",
    "news_synthesizer",
    "market_analysis",
    "portfolio_analysis",
}


def test_rule_router_for_strong_matches():
    """
    Validate that strong, obvious routing cases work correctly
    under the rule-based layer.

    Why this test matters:
        We want to keep deterministic routes stable even after
        introducing the LLM router fallback.
    """
    path = Path("src/data/eval/routing_eval_set.json")

    with path.open("r", encoding="utf-8") as f:
        cases = json.load(f)

    for case in cases:
        user_input = case["input"]
        expected_route = case["expected_route"]

        actual_route = rule_based_route(user_input)

        # Only assert for queries where the rule router can clearly decide.
        if actual_route is not None:
            assert actual_route == expected_route, (
                f"Query '{user_input}' routed to '{actual_route}' "
                f"instead of expected '{expected_route}'"
            )