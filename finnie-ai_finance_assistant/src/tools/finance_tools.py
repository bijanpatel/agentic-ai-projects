import json
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
            JSON string containing market snapshot fields such as:
            - ticker
            - short_name
            - current_price
            - currency
            - day_high
            - day_low
            - previous_close

    Why return JSON string?
        LangChain tools commonly return string-friendly outputs that are easy
        to inject into prompts or agent tool traces.
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
            Time range to fetch.
            Example values: "5d", "1mo", "3mo", "6mo", "1y"

        interval (str):
            Frequency of historical data.
            Example values: "1d", "1wk", "1mo"

    Returns:
        str:
            JSON string containing historical price rows.

    Notes:
        This can become large, so in real production systems you may want to
        summarize or truncate before sending to the LLM.
    """
    history_df = get_price_history(ticker, period=period, interval=interval)
    return history_df.to_json(orient="records", date_format="iso")


@tool
def calculate_portfolio_metrics_tool(portfolio_id: str) -> str:
    """
    Calculate metrics for a sample portfolio.

    Parameters:
        portfolio_id (str):
            Portfolio identifier such as "p1", "p2", "p3".

    Returns:
        str:
            JSON string containing:
            - total value
            - cost basis
            - unrealized gain/loss
            - holdings
            - sector allocation
            - asset type allocation

    Why this tool matters:
        It gives the Portfolio Analysis Agent a structured way to access
        computed portfolio intelligence rather than calling the utility directly.
    """
    df = load_portfolio_data()
    metrics = calculate_portfolio_metrics(df, portfolio_id)
    return json.dumps(metrics, default=str)


@tool
def get_goal_scenarios_tool(user_id: str) -> str:
    """
    Retrieve saved goal-planning scenarios for a user.

    Parameters:
        user_id (str):
            User identifier such as "u1", "u2", "u3".

    Returns:
        str:
            JSON string containing matching goal scenarios.

    Why this tool matters:
        It allows the Goal Planning Agent to use structured scenario data
        in a more agentic and observable way.
    """
    scenarios = get_goal_scenario_by_user(user_id)
    return json.dumps(scenarios, default=str)