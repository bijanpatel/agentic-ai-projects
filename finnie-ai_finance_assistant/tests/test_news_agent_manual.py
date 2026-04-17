from src.agents.news_synthesizer_agent import ask_news_question


def main():
    queries = [
    "Latest US stock market news today",
    "Recent inflation news affecting US markets",
    "Latest Federal Reserve interest rate news and market reaction",
    "Recent bond market news in the US",
    "Latest tech earnings news affecting the stock market"
]

    for query in queries:
        result = ask_news_question(query)
        print("=" * 80)
        print("QUERY:", query)
        print("AGENT:", result.get("agent"))
        print("USED API:", result.get("used_api"))
        print("FALLBACK USED:", result.get("fallback_used"))
        print("ANSWER:\n")
        print(result.get("answer"))
        print("\nSOURCES:")
        for source in result.get("sources", []):
            print(f"- {source['title']} ({source['source']})")


if __name__ == "__main__":
    main()