from src.agents.finance_qa_agent import ask_finance_question
from src.agents.tax_education_agent import ask_tax_question
from src.agents.goal_planning_agent import ask_goal_question
from src.workflow.router import route_query


def router_node(state: dict) -> dict:
    """
    Router node for the workflow.

    Parameters:
        state (dict):
            Shared workflow state. Expected to contain 'user_query'.

    Returns:
        dict:
            Updated state with 'routed_agent'.

    Purpose:
        Decide which agent should handle the current query.
    """
    user_query = state["user_query"]
    state["routed_agent"] = route_query(user_query)
    return state


def finance_qa_node(state: dict) -> dict:
    """
    Finance Q&A node.

    Parameters:
        state (dict):
            Shared workflow state containing 'user_query'.

    Returns:
        dict:
            Updated state with 'result' from the finance agent.
    """
    state["result"] = ask_finance_question(state["user_query"])
    return state


def tax_education_node(state: dict) -> dict:
    """
    Tax Education node.

    Parameters:
        state (dict):
            Shared workflow state containing 'user_query'.

    Returns:
        dict:
            Updated state with 'result' from the tax education agent.
    """
    state["result"] = ask_tax_question(state["user_query"])
    return state


def goal_planning_node(state: dict) -> dict:
    """
    Goal Planning node.

    Parameters:
        state (dict):
            Shared workflow state containing 'user_query'.

    Returns:
        dict:
            Updated state with 'result' from the goal planning agent.
    """
    state["result"] = ask_goal_question(state["user_query"])
    return state