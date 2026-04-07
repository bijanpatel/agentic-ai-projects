from langchain_openai import ChatOpenAI
from src.core.config import load_config
from src.rag.retriever import search_documents


TAX_EDUCATION_SYSTEM_PROMPT = """
You are a beginner-friendly tax education assistant focused on financial education.

Your role:
- Explain tax-related investing concepts clearly and simply.
- Use the retrieved context as your primary source of truth.
- Keep explanations general, educational, and easy to understand.

Important rules:
- Do NOT provide legal or personalized tax advice.
- Do NOT guess jurisdiction-specific tax rules beyond the available context.
- If the retrieved context is limited, say so clearly.
- Focus on concepts such as Roth IRA, 401(k), taxable accounts, and capital gains.

Response style:
- Start with a direct explanation.
- Use simple language.
- Add 2-3 short supporting points if helpful.
"""


def format_context(docs) -> str:
    """
    Convert retrieved documents into a text block for the LLM.

    Parameters:
        docs (list):
            Retrieved document objects from the vector store.

    Returns:
        str:
            A formatted context string containing title, category, source, and content.
    """
    if not docs:
        return "No relevant context was retrieved."

    parts = []
    for i, doc in enumerate(docs, start=1):
        parts.append(
            f"[Document {i}]\n"
            f"Title: {doc.metadata.get('title', 'Untitled')}\n"
            f"Category: {doc.metadata.get('category', 'unknown')}\n"
            f"Source: {doc.metadata.get('source', 'unknown')}\n"
            f"Content: {doc.page_content}\n"
        )
    return "\n".join(parts)


def extract_sources(docs) -> list[dict]:
    """
    Extract unique source references from retrieved documents.

    Parameters:
        docs (list):
            Retrieved document objects.

    Returns:
        list[dict]:
            A list of unique source dictionaries with title and source.
    """
    seen = set()
    sources = []

    for doc in docs:
        title = doc.metadata.get("title", "Untitled")
        source = doc.metadata.get("source", "unknown")
        key = (title, source)

        if key not in seen:
            seen.add(key)
            sources.append({"title": title, "source": source})

    return sources


def ask_tax_question(user_query: str) -> dict:
    """
    Answer a tax education question using retrieved finance knowledge base documents.

    Parameters:
        user_query (str):
            The tax-related question asked by the user.
            Example: "What is a Roth IRA?"

    Returns:
        dict:
            Structured response containing:
            - question
            - answer
            - sources
            - retrieved_doc_count
            - agent
    """
    config = load_config()

    docs = search_documents(
        user_query,
        k=config["rag"]["top_k"]
    )

    if not docs:
        return {
            "question": user_query,
            "answer": "I could not find enough relevant tax education content in the current knowledge base to answer that confidently.",
            "sources": [],
            "retrieved_doc_count": 0,
            "agent": "tax_education",
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

Please answer using the retrieved context only.
Keep the explanation educational and beginner-friendly.
"""

    response = llm.invoke([
        {"role": "system", "content": TAX_EDUCATION_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ])

    return {
        "question": user_query,
        "answer": response.content,
        "sources": sources,
        "retrieved_doc_count": len(docs),
        "agent": "tax_education",
        "used_rag": True,
        "used_api": False,
        "fallback_used": False,
    }