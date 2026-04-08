from src.tools.finance_tools import (
    get_market_snapshot_tool,
    calculate_portfolio_metrics_tool,
    get_goal_scenarios_tool,
)


def main():
    print("\nMARKET SNAPSHOT TOOL")
    print(get_market_snapshot_tool.invoke({"ticker": "AAPL"}))

    print("\nPORTFOLIO METRICS TOOL")
    print(calculate_portfolio_metrics_tool.invoke({"portfolio_id": "p1"}))

    print("\nGOAL SCENARIOS TOOL")
    print(get_goal_scenarios_tool.invoke({"user_id": "u1"}))


if __name__ == "__main__":
    main()