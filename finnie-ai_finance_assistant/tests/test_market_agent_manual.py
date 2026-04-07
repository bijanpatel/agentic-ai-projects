from src.agents.market_analysis_agent import ask_market_question


def main():
    result = ask_market_question(
        user_query="What is Apple stock price today?",
        ticker="AAPL"
    )

    print("\nQUESTION:")
    print(result["question"])

    print("\nANSWER:")
    print(result["answer"])

    print("\nMARKET DATA:")
    print(result["market_data"])

    print("\nAGENT:")
    print(result["agent"])


if __name__ == "__main__":
    main()