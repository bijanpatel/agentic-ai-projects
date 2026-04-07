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


def sector_allocation_chart(sector_allocation: dict):
    """
    Create a bar chart for sector allocation.

    Parameters:
        sector_allocation (dict):
            Dictionary of sector -> value.

    Returns:
        plotly.graph_objs._figure.Figure:
            Bar chart figure.
    """
    df = pd.DataFrame(
        list(sector_allocation.items()),
        columns=["sector", "holding_value"]
    )
    fig = px.bar(
        df,
        x="sector",
        y="holding_value",
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