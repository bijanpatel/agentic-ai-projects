from src.agents.news_synthesizer_agent import ask_news_question


def run_query(query: str, category: str = "all"):
    result = ask_news_question(query, category=category)

    print("=" * 80)
    print("QUERY:", query)
    print("AGENT:", result.get("agent"))
    print("NEWS COUNT:", result.get("news_count"))
    print("ANSWER:\n")
    print(result.get("answer"))
    print("\nSOURCES:")
    for source in result.get("sources", []):
        print(f"- {source['title']} ({source['source']})")


def main():
    run_query("Summarize recent market news for a beginner.")
    run_query("Explain recent inflation-related news simply.", category="inflation")
    run_query("What is happening in bonds recently?", category="fixed_income")


if __name__ == "__main__":
    main()