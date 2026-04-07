from typing import TypedDict, List, Dict, Any

class FinanceAssistantState(TypedDict, total=False):
    messages: List[Dict[str, str]]
    user_query: str
    normalized_query: str
    routed_agent: str
    user_profile: Dict[str, Any]
    risk_tolerance: str
    knowledge_level: str
    goal_context: Dict[str, Any]
    portfolio_context: Dict[str, Any]
    tool_results: Dict[str, Any]
    retrieved_docs: List[Dict[str, Any]]
    final_response: str
    sources: List[str]
    errors: List[str]
    