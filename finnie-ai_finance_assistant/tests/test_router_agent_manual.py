from src.agents.router_agent import llm_route_query


def main():
    queries = [
        "What is an ETF?",
        "What is a Roth IRA?",
        "How should I build an emergency fund?",
        "Summarize recent market news for a beginner.",
        "What is happening with AAPL right now?",
        "Analyze my portfolio and tell me if I am diversified.",
        "I want help figuring out whether my investments are too concentrated.",
    ]

    for query in queries:
        agent = llm_route_query(query)
        print("=" * 80)
        print("QUERY:", query)
        print("SELECTED AGENT:", agent)


if __name__ == "__main__":
    main()