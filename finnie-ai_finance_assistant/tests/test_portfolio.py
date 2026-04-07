from src.utils.portfolio import load_portfolio_data, calculate_portfolio_metrics


def test_portfolio_metrics_for_p1():
    """
    Test that portfolio metrics are calculated correctly for sample portfolio p1.

    Why this test matters:
        Portfolio analysis is one of the required product capabilities.
    """
    df = load_portfolio_data()
    metrics = calculate_portfolio_metrics(df, "p1")

    assert metrics["portfolio_id"] == "p1"
    assert metrics["profile_name"] == "Beginner Balanced"
    assert metrics["total_value"] > 0
    assert metrics["total_cost_basis"] > 0
    assert len(metrics["holdings"]) > 0
    assert "Technology" in metrics["sector_allocation"]


def test_invalid_portfolio_raises_error():
    """
    Test that an invalid portfolio_id raises a ValueError.
    """
    df = load_portfolio_data()

    try:
        calculate_portfolio_metrics(df, "invalid_id")
        assert False, "Expected ValueError for invalid portfolio_id"
    except ValueError:
        assert True