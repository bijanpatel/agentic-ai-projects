from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END

from src.workflow.nodes import (
    router_node,
    finance_qa_node,
    tax_education_node,
    goal_planning_node,
)


class WorkflowState(TypedDict, total=False):
    """
    Shared workflow state passed between LangGraph nodes.

    Fields:
        user_query (str):
            The current user question.

        routed_agent (str):
            The agent selected by the router.

        result (Dict[str, Any]):
            The structured result returned by the selected agent.
    """
    user_query: str
    routed_agent: str
    result: Dict[str, Any]


def decide_next_node(state: WorkflowState) -> str:
    """
    Decide which agent node should run after routing.

    Parameters:
        state (WorkflowState):
            The current workflow state.

    Returns:
        str:
            The name of the next node.
    """
    routed_agent = state.get("routed_agent", "finance_qa")

    if routed_agent == "tax_education":
        return "tax_education"

    if routed_agent == "goal_planning":
        return "goal_planning"

    return "finance_qa"


def build_workflow():
    """
    Build and compile the LangGraph workflow.

    Workflow:
        START -> router -> selected agent -> END

    Returns:
        Compiled graph object that can be invoked with workflow state.
    """
    graph = StateGraph(WorkflowState)

    graph.add_node("router", router_node)
    graph.add_node("finance_qa", finance_qa_node)
    graph.add_node("tax_education", tax_education_node)
    graph.add_node("goal_planning", goal_planning_node)

    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router",
        decide_next_node,
        {
            "finance_qa": "finance_qa",
            "tax_education": "tax_education",
            "goal_planning": "goal_planning",
        }
    )

    graph.add_edge("finance_qa", END)
    graph.add_edge("tax_education", END)
    graph.add_edge("goal_planning", END)

    return graph.compile()