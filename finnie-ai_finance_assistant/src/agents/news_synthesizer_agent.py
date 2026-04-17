import json
from langchain_openai import ChatOpenAI

from src.core.config import load_config
from src.services.news_service import get_news_context


NEWS_SYNTHESIZER_SYSTEM_PROMPT = """
You are a beginner-friendly financial news synthesizer.

Your role:
- Summarize finance news clearly and calmly.
- Explain what the news may mean in simple terms.
- Focus on understanding, not hype.

Important rules:
- Do NOT provide personalized investment advice.
- Do NOT exaggerate or use sensational language.
- Keep the explanation accessible for a beginner.
- If there is limited context, say so clearly.

Response format:
1. Start with a short "Summary" section.
2. Then provide 2 to 4 bullet points under "Key Takeaways".
3. End with a short "Why It Matters" section for a beginner investor.
"""


def ask_news_question(user_query: str, category: str = "all") -> dict:
    """
    Summarize finance news using live search first, then fallback sample data.
    """
    config = load_config()
    news_items, source_mode = get_news_context(user_query)

    if not news_items:
        return {
            "question": user_query,
            "answer": "I could not find relevant finance news right now.",
            "news_count": 0,
            "sources": [],
            "agent": "news_synthesizer",
            "used_rag": False,
            "used_api": False,
            "fallback_used": True,
        }

    llm = ChatOpenAI(
        api_key=config["openai_api_key"],
        model=config["model_name"],
        temperature=config["model"]["temperature"],
    )

    user_prompt = f"""
User question:
{user_query}

News items:
{json.dumps(news_items, indent=2)}

Please answer in this structure:

Summary:
- 2 to 4 sentences explaining the overall news picture.

Key Takeaways:
- 2 to 4 concise bullet points.

Why It Matters:
- 2 to 3 sentences explaining why a beginner investor should care.

Keep the tone calm, educational, and easy to understand.
"""

    response = llm.invoke([
        {"role": "system", "content": NEWS_SYNTHESIZER_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ])

    sources = [
        {
            "title": item.get("title", "Untitled"),
            "source": item.get("source", "Unknown Source"),
        }
        for item in news_items
    ]

    return {
        "question": user_query,
        "answer": response.content,
        "news_count": len(news_items),
        "sources": sources,
        "agent": "news_synthesizer",
        "used_rag": False,
        "used_api": source_mode == "live_search",
        "fallback_used": source_mode != "live_search",
    }