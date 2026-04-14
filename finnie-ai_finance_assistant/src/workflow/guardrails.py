def detect_guardrail_response(user_query: str) -> dict | None:
    """
    Detect whether a user query should trigger a basic guardrail or
    assistant-help response.

    Parameters:
        user_query (str):
            Raw user message.

    Returns:
        dict | None:
            Structured response if a guardrail/help response should trigger,
            otherwise None.

    Implemented handling:
        - greetings / assistant identity / capability questions
        - out-of-domain requests
        - direct buy/sell advice requests
        - unrealistic guaranteed-return requests
    """
    q = user_query.lower().strip()

    # Normalize a little for safer matching
    q_no_punct = (
        q.replace("?", "")
         .replace("!", "")
         .replace(".", "")
         .replace(",", "")
         .strip()
    )

    greeting_keywords = {
        "hi", "hello", "hey", "good morning", "good evening", "good afternoon"
    }

    identity_or_help_phrases = [
        "who are you",
        "what are you",
        "what can you do",
        "help me",
        "help",
        "how are you",
        "what do you do",
    ]

    out_of_domain_keywords = [
        "python inheritance",
        "java spring",
        "sql join",
        "recipe",
        "movie review",
        "weather today",
        "capital of france",
    ]

    direct_advice_keywords = [
        "what stock should i buy",
        "what should i buy tomorrow",
        "tell me what to buy",
        "give me a stock pick",
        "which stock will double",
        "which stock should i buy now",
        "tell me exactly what to buy",
        "best stock to buy tomorrow",
    ]

    guaranteed_return_keywords = [
        "guaranteed return",
        "guaranteed profit",
        "sure shot stock",
        "best stock guaranteed",
        "risk free profit",
        "double my money guaranteed",
    ]

    # 1. Greetings
    if q_no_punct in greeting_keywords:
        return {
            "question": user_query,
            "answer": (
                "Hi! I’m an AI Finance Assistant focused on financial education. "
                "I can help with finance concepts, taxes, goal planning, "
                "portfolio analysis, market context, and financial news."
            ),
            "sources": [],
            "agent": "assistant_help",
            "used_rag": False,
            "used_api": False,
            "fallback_used": False,
            "handoff_used": False,
        }

    # 2. Identity / capability / basic conversational questions
    if any(phrase in q_no_punct for phrase in identity_or_help_phrases):
        return {
            "question": user_query,
            "answer": (
                "I’m an AI Finance Assistant built for financial education. "
                "I can explain finance concepts, tax basics, goal planning, "
                "portfolio analysis, market context, and financial news summaries."
            ),
            "sources": [],
            "agent": "assistant_help",
            "used_rag": False,
            "used_api": False,
            "fallback_used": False,
            "handoff_used": False,
        }

    # 3. Out-of-domain requests
    if any(keyword in q_no_punct for keyword in out_of_domain_keywords):
        return {
            "question": user_query,
            "answer": (
                "I’m currently focused on financial education topics such as "
                "investing basics, taxes, planning, portfolios, market context, "
                "and financial news."
            ),
            "sources": [],
            "agent": "guardrail",
            "used_rag": False,
            "used_api": False,
            "fallback_used": True,
            "handoff_used": False,
        }

    # 4. Direct buy/sell or stock-pick advice
    if any(keyword in q_no_punct for keyword in direct_advice_keywords):
        return {
            "question": user_query,
            "answer": (
                "I can help explain investing concepts, risk, diversification, "
                "and how investors evaluate opportunities, but I can’t tell you "
                "exactly what to buy or sell as personalized financial advice."
            ),
            "sources": [],
            "agent": "guardrail",
            "used_rag": False,
            "used_api": False,
            "fallback_used": True,
            "handoff_used": False,
        }

    # 5. Guaranteed-return claims
    if any(keyword in q_no_punct for keyword in guaranteed_return_keywords):
        return {
            "question": user_query,
            "answer": (
                "There is no guaranteed-return investment in normal market conditions. "
                "I can help explain risk, return tradeoffs, and how investors typically "
                "evaluate opportunities."
            ),
            "sources": [],
            "agent": "guardrail",
            "used_rag": False,
            "used_api": False,
            "fallback_used": True,
            "handoff_used": False,
        }

    return None