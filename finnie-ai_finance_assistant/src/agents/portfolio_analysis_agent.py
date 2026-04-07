from langchain_openai import ChatOpenAI
from src.core.config import load_config
from src.utils.portfolio import load_portfolio_data, calculate_portfolio_metrics


PORTFOLIO_ANALYSIS_SYSTEM_PROMPT = """
You are a beginner-friendly portfolio analysis assistant.

Your role:
- Explain portfolio composition clearly and simply.
- Help the user understand diversification, concentration, and asset mix.
- Use the provided portfolio metrics as the source of truth.

Important rules:
- Do NOT provide personalized investment advice.
- Do NOT recommend buying or selling securities.
- Keep the response educational and easy to understand.
"""


def ask_portfolio_question(user_query: str, portfolio_id: str) -> dict:
    """
    Analyze a sample portfolio and explain the results in beginner-friendly language.

    Parameters:
        user_query (str):
            The user's portfolio-related question.
            Example: "Analyze my portfolio."

        portfolio_id (str):
            The portfolio identifier to analyze.
            Example: "p1"

    Returns:
        dict:
            Structured response containing:
            - question
            - answer
            - portfolio_metrics
            - agent
    """
    config = load_config()

    df = load_portfolio_data()
    metrics = calculate_portfolio_metrics(df, portfolio_id)

    llm = ChatOpenAI(
        api_key=config["openai_api_key"],
        model=config["model_name"],
        temperature=config["model"]["temperature"]
    )

    user_prompt = f"""
User question:
{user_query}

Portfolio metrics:
{metrics}

Explain the portfolio in a simple, educational way for a beginner.
Highlight:
- total value
- diversification observations
- concentration observations
- asset type mix
"""

    response = llm.invoke([
        {"role": "system", "content": PORTFOLIO_ANALYSIS_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ])

    return {
        "question": user_query,
        "answer": response.content,
        "portfolio_metrics": metrics,
        "agent": "portfolio_analysis"
    }