import pandas as pd


def load_portfolio_data(file_path: str = "src/data/sample_portfolios/sample_portfolios.csv") -> pd.DataFrame:
    """
    Load sample portfolio data from CSV.

    Parameters:
        file_path (str):
            Path to the sample portfolios CSV file.

    Returns:
        pd.DataFrame:
            Portfolio holdings data.
    """
    df = pd.read_csv(file_path)
    df.columns = [col.strip() for col in df.columns]
    return df


def calculate_portfolio_metrics(df: pd.DataFrame, portfolio_id: str) -> dict:
    """
    Calculate core metrics for a selected portfolio.

    Parameters:
        df (pd.DataFrame):
            Full portfolio holdings dataframe.

        portfolio_id (str):
            Portfolio identifier to analyze.
            Example: "p1", "p2"

    Returns:
        dict:
            Structured portfolio metrics including:
            - portfolio_id
            - profile_name
            - total_value
            - total_cost_basis
            - unrealized_gain_loss
            - holdings (with allocation %)
            - sector_allocation
            - asset_type_allocation

    Core formulas:
        holding_value = quantity * current_price
        cost_basis = quantity * avg_buy_price
        unrealized_gain_loss = holding_value - cost_basis
        allocation_percent = holding_value / total_portfolio_value * 100
    """
    portfolio_df = df[df["portfolio_id"] == portfolio_id].copy()

    if portfolio_df.empty:
        raise ValueError(f"No portfolio found for portfolio_id='{portfolio_id}'")

    portfolio_df["holding_value"] = portfolio_df["quantity"] * portfolio_df["current_price"]
    portfolio_df["cost_basis"] = portfolio_df["quantity"] * portfolio_df["avg_buy_price"]
    portfolio_df["unrealized_gain_loss"] = portfolio_df["holding_value"] - portfolio_df["cost_basis"]

    total_value = portfolio_df["holding_value"].sum()
    total_cost_basis = portfolio_df["cost_basis"].sum()
    total_gain_loss = portfolio_df["unrealized_gain_loss"].sum()

    portfolio_df["allocation_percent"] = (portfolio_df["holding_value"] / total_value) * 100

    sector_allocation = (
        portfolio_df.groupby("sector")["holding_value"]
        .sum()
        .sort_values(ascending=False)
        .to_dict()
    )

    asset_type_allocation = (
        portfolio_df.groupby("asset_type")["holding_value"]
        .sum()
        .sort_values(ascending=False)
        .to_dict()
    )

    holdings = portfolio_df[
        [
            "ticker",
            "asset_type",
            "quantity",
            "avg_buy_price",
            "current_price",
            "holding_value",
            "cost_basis",
            "unrealized_gain_loss",
            "allocation_percent",
            "sector",
        ]
    ].to_dict(orient="records")

    return {
        "portfolio_id": portfolio_id,
        "profile_name": portfolio_df["profile_name"].iloc[0],
        "total_value": round(total_value, 2),
        "total_cost_basis": round(total_cost_basis, 2),
        "unrealized_gain_loss": round(total_gain_loss, 2),
        "holdings": holdings,
        "sector_allocation": sector_allocation,
        "asset_type_allocation": asset_type_allocation,
    }