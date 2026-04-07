from src.agents.finance_qa_agent import ask_finance_question


def main():
    query = "What is an JAVA?"
    result = ask_finance_question(query)

    print("\nQUESTION:")
    print(result["question"])

    print("\nANSWER:")
    print(result["answer"])

    print("\nSOURCES:")
    for source in result["sources"]:
        print(f"- {source['title']} ({source['source']})")

    print(f"\nRetrieved documents: {result['retrieved_doc_count']}")


if __name__ == "__main__":
    main()