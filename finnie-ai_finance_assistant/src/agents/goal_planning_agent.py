import json
from langchain_openai import ChatOpenAI

from src.core.config import load_config
from src.rag.retriever import search_documents
from src.tools.finance_tools import get_goal_scenarios_tool


GOAL_PLANNING_SYSTEM_PROMPT = """
You are a beginner-friendly financial goal planning assistant.

Your role:
- Help users think through savings and investing goals in an educational way.
- Use retrieved educational context as a grounding source.
- Use available goal scenario data when provided.
- Explain concepts such as emergency funds, time horizon, risk tolerance, and consistent contributions.

Important rules:
- Do NOT provide personalized financial advice.
- Do NOT promise investment outcomes.
- If context is limited, say so clearly.
- Keep the response practical, simple, and educational.

Response style:
- Start with a direct answer.
- Use simple planning-oriented language.
- Include 2-4 practical points if helpful.
"""


def format_context(docs) -> str:
    """
    Convert retrieved documents into a prompt-ready context block.
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


def ask_goal_question(user_query: str, user_id: str = "u1") -> dict:
    """
    Answer a goal-planning question using both RAG and goal scenario tool data.

    Parameters:
        user_query (str):
            Goal-planning question.

        user_id (str):
            User identifier for scenario lookup.

    Returns:
        dict:
            Structured goal-planning response.
    """
    config = load_config()

    docs = search_documents(
        user_query,
        k=config["rag"]["top_k"]
    )

    scenarios_json = get_goal_scenarios_tool.invoke({"user_id": user_id})
    scenarios = json.loads(scenarios_json)

    if not docs and not scenarios:
        return {
            "question": user_query,
            "answer": "I could not find enough relevant goal-planning content or saved scenario data to answer that confidently.",
            "sources": [],
            "retrieved_doc_count": 0,
            "agent": "goal_planning",
            "used_rag": False,
            "used_api": False,
            "fallback_used": True,
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

Relevant educational context:
{context}

Saved goal scenarios for this user:
{json.dumps(scenarios, indent=2)}

Answer in a beginner-friendly way.
If scenarios are relevant, use them to make the explanation more concrete.
Keep the response educational, not advisory.
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
        "goal_scenarios_used": len(scenarios),
        "agent": "goal_planning",
        "used_rag": len(docs) > 0,
        "used_api": False,
        "fallback_used": False,
    }