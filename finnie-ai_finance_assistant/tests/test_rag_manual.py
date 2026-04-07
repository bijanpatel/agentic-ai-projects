from src.rag.retriever import search_documents


def main():
    query = "What is an ETF?"
    docs = search_documents(query, k=3)

    print(f"\nQuery: {query}\n")
    for i, doc in enumerate(docs, start=1):
        print(f"Result {i}")
        print("Title:", doc.metadata.get("title"))
        print("Category:", doc.metadata.get("category"))
        print("Source:", doc.metadata.get("source"))
        print("Content:", doc.page_content)
        print("-" * 80)


if __name__ == "__main__":
    main()