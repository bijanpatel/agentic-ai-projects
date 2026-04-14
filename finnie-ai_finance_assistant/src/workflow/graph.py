from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END

from src.workflow.nodes import (
    router_node,
    finance_qa_node,
    tax_education_node,
    goal_planning_node,
    news_synthesizer_node,
    market_analysis_node,
    portfolio_analysis_node,
    news_to_market_node,
    portfolio_to_finance_node,
    goal_to_tax_node,
)


class WorkflowState(TypedDict, total=False):
    """
    Shared workflow state passed between LangGraph nodes.
    """
    user_query: str
    routed_agent: str
    result: Dict[str, Any]
    primary_result: Dict[str, Any]
    handoff_to: str | None


def decide_primary_node(state: WorkflowState) -> str:
    routed_agent = state.get("routed_agent", "finance_qa")

    if routed_agent == "tax_education":
        return "tax_education"
    if routed_agent == "goal_planning":
        return "goal_planning"
    if routed_agent == "news_synthesizer":
        return "news_synthesizer"
    if routed_agent == "market_analysis":
        return "market_analysis"
    if routed_agent == "portfolio_analysis":
        return "portfolio_analysis"
    if routed_agent == "guardrail":
        return "guardrail"

    return "finance_qa"


def decide_after_primary(state: WorkflowState) -> str:
    """
    Decide whether to trigger one of the explicit A2A-lite handoff nodes.
    """
    handoff_to = state.get("handoff_to")
    primary_agent = state.get("routed_agent")

    if primary_agent == "news_synthesizer" and handoff_to == "market_analysis":
        return "news_to_market"

    if primary_agent == "portfolio_analysis" and handoff_to == "finance_qa":
        return "portfolio_to_finance"

    if primary_agent == "goal_planning" and handoff_to == "tax_education":
        return "goal_to_tax"

    return "end"


def build_workflow():
    """
    Build and compile the LangGraph workflow with explicit A2A-lite handoffs.
    """
    graph = StateGraph(WorkflowState)

    graph.add_node("router", router_node)
    graph.add_node("finance_qa", finance_qa_node)
    graph.add_node("tax_education", tax_education_node)
    graph.add_node("goal_planning", goal_planning_node)
    graph.add_node("news_synthesizer", news_synthesizer_node)
    graph.add_node("market_analysis", market_analysis_node)
    graph.add_node("portfolio_analysis", portfolio_analysis_node)

    graph.add_node("news_to_market", news_to_market_node)
    graph.add_node("portfolio_to_finance", portfolio_to_finance_node)
    graph.add_node("goal_to_tax", goal_to_tax_node)
    graph.add_node("guardrail", lambda state: state)

    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router",
        decide_primary_node,
        {
            "finance_qa": "finance_qa",
            "tax_education": "tax_education",
            "goal_planning": "goal_planning",
            "news_synthesizer": "news_synthesizer",
            "market_analysis": "market_analysis",
            "portfolio_analysis": "portfolio_analysis",
            "guardrail": "guardrail",
        }
    )

    for node_name in [
        "finance_qa",
        "tax_education",
        "goal_planning",
        "news_synthesizer",
        "market_analysis",
        "portfolio_analysis",
    ]:
        graph.add_conditional_edges(
            node_name,
            decide_after_primary,
            {
                "news_to_market": "news_to_market",
                "portfolio_to_finance": "portfolio_to_finance",
                "goal_to_tax": "goal_to_tax",
                "end": END,
            }
        )

    graph.add_edge("news_to_market", END)
    graph.add_edge("portfolio_to_finance", END)
    graph.add_edge("goal_to_tax", END)
    graph.add_edge("guardrail", END)

    return graph.compile()