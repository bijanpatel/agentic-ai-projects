from langchain_openai import ChatOpenAI
from src.core.config import load_config


ROUTER_SYSTEM_PROMPT = """
You are a routing agent for a financial education assistant.

Your job is to choose the single best agent for the user's query.

Available agents:
1. finance_qa
   - General finance education questions
   - Concepts like ETF, stocks, bonds, diversification, inflation, compound interest

2. tax_education
   - Tax-related investing and retirement questions
   - Roth IRA, 401(k), capital gains, taxable vs tax-advantaged accounts

3. goal_planning
   - Savings and planning questions
   - Emergency fund, retirement planning, saving for a house, time horizon, risk tolerance

4. news_synthesizer
   - Finance and market news summarization
   - Headlines, recent market news, what happened in markets

5. market_analysis
   - Live market/ticker questions
   - Stock price, current market behavior, ticker analysis, what is happening with AAPL

6. portfolio_analysis
   - Portfolio composition and diversification questions
   - Portfolio analysis, holdings, asset allocation, concentration, diversification of investments

Rules:
- Choose exactly one agent.
- Return only the agent name.
- Do not explain your reasoning.
- Do not return anything except one valid agent name.
"""


def llm_route_query(user_query: str) -> str:
    """
    Use the LLM as a routing agent to select the best specialized agent.

    Parameters:
        user_query (str):
            The user's question.

    Returns:
        str:
            One of:
            - finance_qa
            - tax_education
            - goal_planning
            - news_synthesizer
            - market_analysis
            - portfolio_analysis

    Why this function exists:
        It allows the system to route more flexibly than keyword matching alone.
    """
    config = load_config()

    llm = ChatOpenAI(
        api_key=config["openai_api_key"],
        model=config["model_name"],
        temperature=0.0,  # deterministic routing is preferred
    )

    response = llm.invoke([
        {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
        {"role": "user", "content": f"User query:\n{user_query}"}
    ])

    selected_agent = response.content.strip()

    valid_agents = {
        "finance_qa",
        "tax_education",
        "goal_planning",
        "news_synthesizer",
        "market_analysis",
        "portfolio_analysis",
    }

    if selected_agent not in valid_agents:
        return "finance_qa"

    return selected_agent