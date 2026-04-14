import json
from pathlib import Path
from langchain.tools import tool

from src.utils.market_data import get_ticker_snapshot, get_price_history
from src.utils.portfolio import load_portfolio_data, calculate_portfolio_metrics
from src.utils.goals import get_goal_scenario_by_user


@tool
def get_market_snapshot_tool(ticker: str) -> str:
    """
    Fetch a live market snapshot for a ticker.

    Parameters:
        ticker (str):
            Stock or ETF ticker symbol.
            Example: "AAPL", "VOO", "MSFT"

    Returns:
        str:
            JSON string containing market snapshot data.

    Why JSON string?
        Tools are often easiest to pass into prompts and logs as serialized text.
    """
    snapshot = get_ticker_snapshot(ticker)
    return json.dumps(snapshot, default=str)


@tool
def get_price_history_tool(ticker: str, period: str = "1mo", interval: str = "1d") -> str:
    """
    Fetch historical price data for a ticker.

    Parameters:
        ticker (str):
            Stock or ETF ticker symbol.

        period (str):
            Time period to fetch, such as "1mo" or "3mo".

        interval (str):
            Data interval such as "1d" or "1wk".

    Returns:
        str:
            JSON string of historical price rows.
    """
    history_df = get_price_history(ticker, period=period, interval=interval)
    return history_df.to_json(orient="records", date_format="iso")


@tool
def calculate_portfolio_metrics_tool(portfolio_id: str) -> str:
    """
    Calculate metrics for a sample portfolio.

    Parameters:
        portfolio_id (str):
            Portfolio identifier, such as "p1" or "p2".

    Returns:
        str:
            JSON string containing portfolio metrics.
    """
    df = load_portfolio_data()
    metrics = calculate_portfolio_metrics(df, portfolio_id)
    return json.dumps(metrics, default=str)


@tool
def get_goal_scenarios_tool(user_id: str) -> str:
    """
    Retrieve goal-planning scenarios for a user.

    Parameters:
        user_id (str):
            User identifier such as "u1".

    Returns:
        str:
            JSON string containing the user's goal scenarios.
    """
    scenarios = get_goal_scenario_by_user(user_id)
    return json.dumps(scenarios, default=str)


@tool
def get_sample_finance_news_tool(category: str = "all") -> str:
    """
    Retrieve sample finance news items from the local news dataset.

    Parameters:
        category (str):
            Optional category filter such as:
            - "all"
            - "markets"
            - "equities"
            - "fixed_income"

    Returns:
        str:
            JSON string containing matching news items.

    Why this tool matters:
        It gives the News Synthesizer Agent a structured news source without
        requiring live web ingestion in this milestone.
    """
    path = Path("src/data/news/sample_finance_news.json")

    with path.open("r", encoding="utf-8") as f:
        news_items = json.load(f)

    if category != "all":
        news_items = [item for item in news_items if item.get("category") == category]

    return json.dumps(news_items, default=str)