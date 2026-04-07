import json
from pathlib import Path


def load_goal_scenarios(file_path: str = "src/data/eval/goal_scenarios.json") -> list[dict]:
    """
    Load predefined goal-planning scenarios.

    Parameters:
        file_path (str):
            Path to the goal scenarios JSON file.

    Returns:
        list[dict]:
            Goal scenario records.
    """
    path = Path(file_path)

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_goal_scenario_by_user(user_id: str) -> list[dict]:
    """
    Return all goal scenarios for a given user_id.

    Parameters:
        user_id (str):
            Example: "u1"

    Returns:
        list[dict]:
            Matching goal scenarios.
    """
    scenarios = load_goal_scenarios()
    return [scenario for scenario in scenarios if scenario["user_id"] == user_id]