from typing import TypedDict, Dict, Any, List, Optional


class WorkflowState(TypedDict, total=False):
    """
    Shared workflow state for the assistant.

    Fields:
        user_query:
            The user's current message.

        messages:
            Conversation history as a list of role/content dicts.

        routed_agent:
            The agent selected by the router.

        last_agent:
            The most recent agent that handled the conversation.

        result:
            Final structured response for the current turn.

        primary_result:
            Stored primary agent result before any handoff.

        handoff_to:
            Secondary agent name if an A2A-lite handoff is needed.

        portfolio_context:
            Partial or complete structured portfolio information gathered from chat.

        goal_context:
            Partial or complete structured goal-planning context.

        risk_tolerance:
            User-provided risk preference if known.

        needs_followup:
            Whether the system needs additional input before continuing.

        followup_type:
            What kind of follow-up is needed, such as:
            - portfolio_holdings
            - portfolio_cost_basis
            - ticker_clarification
    """
    user_query: str
    messages: List[Dict[str, str]]
    routed_agent: str
    last_agent: str
    result: Dict[str, Any]
    primary_result: Dict[str, Any]
    handoff_to: Optional[str]
    portfolio_context: Dict[str, Any]
    goal_context: Dict[str, Any]
    risk_tolerance: str
    needs_followup: bool
    followup_type: str