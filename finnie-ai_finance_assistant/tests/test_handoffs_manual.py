from src.workflow.graph import build_workflow


def run_query(query: str):
    app = build_workflow()
    result = app.invoke({"user_query": query})

    print("=" * 80)
    print("QUERY:", query)
    print("ROUTED AGENT:", result.get("routed_agent"))
    print("HANDOFF TO:", result.get("handoff_to"))
    print("FINAL AGENT:", result.get("result", {}).get("agent"))
    print("ANSWER:\n", result.get("result", {}).get("answer"))


def main():
    run_query("Summarize recent market news about AAPL for a beginner.")
    run_query("Analyze my portfolio and explain diversification.")
    run_query("Help me plan for retirement and explain Roth IRA versus 401(k).")


if __name__ == "__main__":
    main()