from src.workflow.graph import build_workflow


def run_query(query: str):
    """
    Run one test query through the workflow and print the result.
    """
    app = build_workflow()
    result = app.invoke({"user_query": query})

    print("\n" + "=" * 80)
    print("QUERY:", query)
    print("ROUTED AGENT:", result.get("routed_agent"))
    print("ANSWER:\n", result["result"]["answer"])
    print("SOURCES:")
    for source in result["result"].get("sources", []):
        print(f"- {source['title']} ({source['source']})")


def main():
    run_query("What is an ETF?")
    run_query("What is a Roth IRA?")
    run_query("How should I build an emergency fund?")
    run_query("Summarize recent market news for a beginner.")


if __name__ == "__main__":
    main()