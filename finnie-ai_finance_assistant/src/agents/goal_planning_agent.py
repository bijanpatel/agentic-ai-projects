from langchain_openai import ChatOpenAI
from src.core.config import load_config
from src.rag.retriever import search_documents


GOAL_PLANNING_SYSTEM_PROMPT = """
You are a beginner-friendly financial goal planning assistant.

Your role:
- Help users think through savings and investing goals in an educational way.
- Use the retrieved context as your primary source of truth.
- Explain concepts such as emergency funds, time horizon, risk tolerance, and consistent contributions.

Important rules:
- Do NOT provide personalized financial advice.
- Do NOT promise investment outcomes.
- If the retrieved context is limited, say so clearly.
- Keep the response practical, simple, and educational.

Response style:
- Start with a direct answer.
- Use simple planning-oriented language.
- Include 2-4 practical points if helpful.
"""


def format_context(docs) -> str:
    """
    Convert retrieved documents into a text block for the LLM.

    Parameters:
        docs (list):
            Retrieved document objects from the vector store.

    Returns:
        str:
            Formatted context string for prompting the LLM.
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
            A list of unique source dictionaries.
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


def ask_goal_question(user_query: str) -> dict:
    """
    Answer a goal-planning question using retrieved finance knowledge base documents.

    Parameters:
        user_query (str):
            The goal-planning question asked by the user.
            Example: "How should I build an emergency fund?"

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
            "answer": "I could not find enough relevant goal-planning content in the current knowledge base to answer that confidently.",
            "sources": [],
            "retrieved_doc_count": 0,
            "agent": "goal_planning"
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
Keep the explanation educational, practical, and beginner-friendly.
"""

    response = llm.invoke([
        {"role": "system", "content": GOAL_PLANNING_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ])

    return {
        "question": user_query,
        "answer": response.content,
        "sources": sources,
        "retrieved_doc_count": len(docs),
        "agent": "goal_planning"
    }