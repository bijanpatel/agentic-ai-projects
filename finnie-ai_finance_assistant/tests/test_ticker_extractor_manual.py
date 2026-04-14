from src.agents.ticker_extractor_agent import extract_ticker_hybrid


def main():
    queries = [
        "What is happening with Apple today?",
        "How is Microsoft doing right now?",
        "Tell me about Tesla stock",
        "What is happening with AAPL?",
        "Show me the latest on VOO",
        "What is the current price of Nvidia?",
        "How is the market doing?"
    ]

    for query in queries:
        ticker = extract_ticker_hybrid(query)
        print("=" * 80)
        print("QUERY:", query)
        print("EXTRACTED TICKER:", ticker)


if __name__ == "__main__":
    main()