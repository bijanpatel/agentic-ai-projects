import json
from langchain_openai import ChatOpenAI

from src.core.config import load_config
from src.tools.finance_tools import get_sample_finance_news_tool


NEWS_SYNTHESIZER_SYSTEM_PROMPT = """
    You are a beginner-friendly financial news synthesizer.

    Your role:
    - Summarize finance news clearly and calmly.
    - Explain what the news may mean in simple terms.
    - Use the provided news items as your source of truth.
    - Focus on understanding, not hype.

    Important rules:
    - Do NOT provide personalized investment advice.
    - Do NOT exaggerate or use sensational language.
    - Keep the explanation accessible for a beginner.
    - If there is limited news context, say so clearly.

    Response format:
    1. Start with a short "Summary" section.
    2. Then provide 2 to 4 bullet points under "Key Takeaways".
    3. End with a short "Why It Matters" section for a beginner investor.

    Tone:
    - calm
    - educational
    - clear
    - concise
"""


def ask_news_question(user_query: str, category: str = "all") -> dict:
    """
    Summarize finance news using the local news tool.

    Parameters:
        user_query (str):
            The user's news-related question.
            Example: "Summarize today's market news for a beginner."

        category (str):
            Optional category filter for the news tool.

    Returns:
        dict:
            Structured response containing:
            - question
            - answer
            - news_count
            - sources
            - agent
            - used_rag
            - used_api
            - fallback_used
    """
    config = load_config()

    news_json = get_sample_finance_news_tool.invoke({"category": category})
    news_items = json.loads(news_json)

    if not news_items:
        return {
            "question": user_query,
            "answer": "I could not find relevant finance news in the current news dataset.",
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
        temperature=config["model"]["temperature"]
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
        {"role": "user", "content": user_prompt}
    ])

    sources = [
        {
            "title": item.get("title", "Untitled"),
            "source": item.get("source", "Unknown Source")
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
        "used_api": False,
        "fallback_used": False,
    }