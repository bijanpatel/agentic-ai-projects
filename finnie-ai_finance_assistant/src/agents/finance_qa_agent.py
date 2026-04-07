from langchain_openai import ChatOpenAI
from src.core.config import load_config
from src.core.prompts import FINANCE_QA_SYSTEM_PROMPT
from src.rag.retriever import search_documents


def format_context(docs) -> str:
    if not docs:
        return "No relevant context was retrieved."

    context_parts = []
    for i, doc in enumerate(docs, start=1):
        title = doc.metadata.get("title", "Untitled")
        category = doc.metadata.get("category", "unknown")
        source = doc.metadata.get("source", "unknown")
        content = doc.page_content

        context_parts.append(
            f"[Document {i}]\n"
            f"Title: {title}\n"
            f"Category: {category}\n"
            f"Source: {source}\n"
            f"Content: {content}\n"
        )

    return "\n".join(context_parts)


def extract_sources(docs) -> list[dict]:
    sources = []
    seen = set()

    for doc in docs:
        title = doc.metadata.get("title", "Untitled")
        source = doc.metadata.get("source", "unknown")
        key = (title, source)

        if key not in seen:
            seen.add(key)
            sources.append({
                "title": title,
                "source": source
            })

    return sources


def ask_finance_question(user_query: str) -> dict:
    config = load_config()

    docs = search_documents(user_query, k=config["rag"]["top_k"])
    if not docs:
        return {
            "question": user_query,
            "answer": "I could not find enough relevant finance knowledge in the current knowledge base to answer that confidently.",
            "sources": [],
            "retrieved_doc_count": 0,
            "agent": "finance_qa",
            "used_rag": True,
            "used_api": False,
            "fallback_used": False,
        }
    context = format_context(docs)
    sources = extract_sources(docs)

    llm = ChatOpenAI(
        api_key=config["openai_api_key"],
        model=config["model_name"],
        temperature=config["model"]["temperature"]
    )

    user_prompt = f"""
User question:
{user_query}

Retrieved context:
{context}

Please answer the user using the retrieved context.
If relevant, keep the explanation beginner-friendly and educational.
"""

    response = llm.invoke([
        {"role": "system", "content": FINANCE_QA_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ])

    return {
        "question": user_query,
        "answer": response.content,
        "sources": sources,
        "retrieved_doc_count": len(docs),
        "agent": "finance_qa",
        "used_rag": True,
        "used_api": False,
        "fallback_used": False,
    }