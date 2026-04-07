from src.agents.portfolio_analysis_agent import ask_portfolio_question


def main():
    result = ask_portfolio_question(
        user_query="Analyze this sample portfolio for a beginner.",
        portfolio_id="p1"
    )

    print("\nQUESTION:")
    print(result["question"])

    print("\nANSWER:")
    print(result["answer"])

    print("\nPORTFOLIO METRICS:")
    print(result["portfolio_metrics"])

    print("\nAGENT:")
    print(result["agent"])


if __name__ == "__main__":
    main()