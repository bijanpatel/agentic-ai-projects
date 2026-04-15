import pandas as pd
import plotly.express as px


def portfolio_allocation_chart(holdings: list):
    """
    Create a pie chart for portfolio holding allocation.

    Parameters:
        holdings (list):
            List of holding dictionaries from portfolio metrics.

    Returns:
        plotly.graph_objs._figure.Figure:
            Pie chart figure.
    """
    df = pd.DataFrame(holdings)
    fig = px.pie(
        df,
        names="ticker",
        values="holding_value",
        title="Portfolio Allocation by Holding"
    )
    return fig


def sector_allocation_chart(sector_allocation):
    """
    Create a sector allocation chart.

    Supports either:
    - dict format:
        {"Technology": 4200, "Healthcare": 1800}
    - list-of-dicts format:
        [
            {"sector": "Technology", "value": 4200, "allocation_pct": 55.0},
            {"sector": "Healthcare", "value": 1800, "allocation_pct": 23.0},
        ]
    """
    import pandas as pd
    import plotly.express as px

    if isinstance(sector_allocation, dict):
        df = pd.DataFrame(
            [
                {"sector": sector, "value": value}
                for sector, value in sector_allocation.items()
            ]
        )
    elif isinstance(sector_allocation, list):
        df = pd.DataFrame(sector_allocation)

        # Normalize expected column names if needed
        if "sector" not in df.columns or "value" not in df.columns:
            raise ValueError(
                "Sector allocation list must contain 'sector' and 'value' fields."
            )
    else:
        raise ValueError("sector_allocation must be either a dict or a list of dicts.")

    fig = px.pie(
        df,
        names="sector",
        values="value",
        title="Sector Allocation"
    )
    return fig


def price_history_chart(history_df, ticker: str):
    """
    Create a line chart for historical closing prices.

    Parameters:
        history_df (pd.DataFrame):
            Historical price dataframe from yfinance.

        ticker (str):
            Ticker symbol for chart title.

    Returns:
        plotly.graph_objs._figure.Figure:
            Line chart figure.
    """
    fig = px.line(
        history_df,
        x="Date",
        y="Close",
        title=f"{ticker.upper()} Price History"
    )
    return fig