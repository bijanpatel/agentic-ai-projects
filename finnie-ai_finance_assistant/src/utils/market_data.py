import yfinance as yf
import pandas as pd


def get_ticker_snapshot(ticker: str) -> dict:
    """
    Fetch a snapshot of current market information for a ticker.

    Parameters:
        ticker (str):
            Stock or ETF ticker symbol.
            Example: "AAPL", "VOO", "MSFT"

    Returns:
        dict:
            A dictionary containing:
            - ticker
            - short_name
            - current_price
            - currency
            - day_high
            - day_low
            - previous_close

    Notes:
        This uses yfinance, which is convenient for MVP/demo use.
        In production, live market data may need more robust vendor APIs and fallback logic.
    """
    t = yf.Ticker(ticker)
    info = t.info

    return {
        "ticker": ticker.upper(),
        "short_name": info.get("shortName"),
        "current_price": info.get("currentPrice"),
        "currency": info.get("currency"),
        "day_high": info.get("dayHigh"),
        "day_low": info.get("dayLow"),
        "previous_close": info.get("previousClose"),
    }


def get_price_history(ticker: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
    """
    Fetch historical price data for a ticker.

    Parameters:
        ticker (str):
            Stock or ETF ticker symbol.

        period (str):
            Time range to fetch.
            Common values:
            - "5d"
            - "1mo"
            - "3mo"
            - "6mo"
            - "1y"

        interval (str):
            Frequency of price data.
            Common values:
            - "1d"  -> daily
            - "1wk" -> weekly
            - "1mo" -> monthly

    Returns:
        pd.DataFrame:
            Historical OHLCV data indexed by date.

    Why this matters:
        This will later support market charts in the Streamlit UI.
    """
    t = yf.Ticker(ticker)
    history = t.history(period=period, interval=interval)
    return history.reset_index()