import os
import sys
import streamlit as st
import pandas as pd

# Add project root to Python path so `src.*` imports work when running Streamlit directly.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.core.config import load_config
from src.workflow.graph import build_workflow
from src.agents.portfolio_analysis_agent import ask_portfolio_question
from src.agents.market_analysis_agent import ask_market_question
from src.utils.portfolio import load_portfolio_data
from src.utils.market_data import get_price_history
from src.utils.evaluation import log_interaction
from src.web_app.charts import (
    portfolio_allocation_chart,
    sector_allocation_chart,
    price_history_chart,
)


def render_starter_prompts():
    """
    Render compact starter prompts when the chat is empty.

    Returns:
        str | None:
            Selected starter prompt if clicked, otherwise None.
    """
    c1, c2, c3, c4 = st.columns(4)

    selected_prompt = None

    with c1:
        if st.button("What is an ETF?", use_container_width=True):
            selected_prompt = "What is an ETF?"

    with c2:
        if st.button("Roth IRA basics", use_container_width=True):
            selected_prompt = "What is a Roth IRA?"

    with c3:
        if st.button("Analyze my portfolio", use_container_width=True):
            selected_prompt = "Analyze my portfolio"

    with c4:
        if st.button("Market news summary", use_container_width=True):
            selected_prompt = "Summarize recent market news for a beginner."

    return selected_prompt


def render_response_details_icon(metadata: dict):
    """
    Render a tiny inline info icon with a hover tooltip.
    This avoids Streamlit popover/button chrome and avoids broken HTML tags.
    """
    if not metadata:
        return

    agent = metadata.get("routed_agent", "unknown")
    used_rag = metadata.get("used_rag", False)
    used_api = metadata.get("used_api", False)
    fallback_used = metadata.get("fallback_used", False)
    needs_followup = metadata.get("needs_followup", False)
    followup_type = metadata.get("followup_type", "")
    sources = metadata.get("sources", [])

    lines = [
        f"Agent: {agent}",
        f"Used RAG: {used_rag}",
        f"Used API: {used_api}",
        f"Fallback: {fallback_used}",
    ]

    if needs_followup:
        lines.append(f"Needs Follow-up: {needs_followup}")
        lines.append(f"Follow-up Type: {followup_type}")

    if sources:
        lines.append("Sources:")
        for src in sources[:4]:
            lines.append(f"- {src['title']} ({src['source']})")

    tooltip_text = "&#10;".join(
        line.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")
        for line in lines
    )

    st.markdown(
        f"""
        <div style="display:flex; justify-content:flex-end; align-items:flex-start; margin-top:0.15rem;">
            <span title="{tooltip_text}"
                  style="cursor:help; color:#6b7280; font-size:1rem; line-height:1;">
                ⓘ
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_sticky_header(title: str):
    """
    Render a sticky page header.
    """
    st.markdown(
        f"""
        <style>
        .sticky-app-header {{
            position: sticky;
            top: 0;
            z-index: 999;
            background: white;
            padding: 1rem 0 0.75rem 0;
            margin-bottom: 0.5rem;
            border-bottom: 1px solid #f1f5f9;
        }}

        .sticky-app-title {{
            font-size: 3rem;
            font-weight: 700;
            line-height: 1.1;
            color: #111827;
            margin: 0;
        }}
        </style>

        <div class="sticky-app-header">
            <div class="sticky-app-title">{title}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def chat_tab():
    """
    Render the main assistant chat view.
    """
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    starter_prompt = None
    if not st.session_state.chat_messages:
        st.caption("Try one")
        starter_prompt = render_starter_prompts()
        st.divider()

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                text_col, icon_col = st.columns([24, 1], vertical_alignment="top")
                with text_col:
                    st.write(message["content"])
                with icon_col:
                    metadata = message.get("metadata", {})
                    if metadata:
                        render_response_details_icon(metadata)
            else:
                st.write(message["content"])

    user_query = st.chat_input(
        "Ask anything about finance, tax, planning, portfolios, markets, or news"
    )

    final_query = user_query or starter_prompt

    if final_query:
        st.session_state.chat_messages.append({
            "role": "user",
            "content": final_query,
        })

        app = build_workflow()
        result = app.invoke({
            "user_query": final_query,
            "messages": st.session_state.chat_messages,
        })

        routed_agent = result.get("routed_agent", "unknown")
        agent_result = result.get("result", {})

        answer = agent_result.get("answer", "No answer returned.")
        sources = agent_result.get("sources", [])

        assistant_metadata = {
            "routed_agent": routed_agent,
            "used_rag": agent_result.get("used_rag", False),
            "used_api": agent_result.get("used_api", False),
            "fallback_used": agent_result.get("fallback_used", False),
            "needs_followup": result.get("needs_followup", False),
            "followup_type": result.get("followup_type", ""),
            "sources": sources,
        }

        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": answer,
            "metadata": assistant_metadata,
        })

        log_interaction({
            "user_query": final_query,
            "agent": agent_result.get("agent", routed_agent),
            "used_rag": agent_result.get("used_rag", False),
            "used_api": agent_result.get("used_api", False),
            "fallback_used": agent_result.get("fallback_used", False),
            "retrieved_doc_count": agent_result.get("retrieved_doc_count", 0),
            "needs_followup": result.get("needs_followup", False),
            "followup_type": result.get("followup_type", ""),
        })

        st.rerun()


def portfolio_tab():
    """
    Render the Portfolio Explorer view.
    """
    st.subheader("Portfolio Explorer")
    st.caption("Choose a sample portfolio and review a beginner-friendly explanation.")

    df = load_portfolio_data()

    portfolio_options = (
        df[["portfolio_id", "profile_name"]]
        .drop_duplicates()
        .sort_values("portfolio_id")
    )

    portfolio_map = {
        f"{row['portfolio_id']} - {row['profile_name']}": row["portfolio_id"]
        for _, row in portfolio_options.iterrows()
    }

    selected_label = st.selectbox(
        "Choose a portfolio",
        options=list(portfolio_map.keys()),
        key="portfolio_select",
    )

    if st.button("Analyze Portfolio", key="portfolio_submit"):
        portfolio_id = portfolio_map[selected_label]

        result = ask_portfolio_question(
            user_query="Analyze this portfolio for a beginner investor.",
            portfolio_id=portfolio_id,
        )

        st.markdown("### Portfolio Explanation")
        st.write(result["answer"])

        metrics = result["portfolio_metrics"]

        total_value = float(metrics["total_value"])
        total_cost_basis = float(metrics["total_cost_basis"])
        unrealized_gain_loss = float(metrics["unrealized_gain_loss"])

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Value", f"${total_value:,.2f}")
        col2.metric("Total Cost Basis", f"${total_cost_basis:,.2f}")
        col3.metric("Unrealized Gain/Loss", f"${unrealized_gain_loss:,.2f}")

        st.markdown("### Allocation by Holding")
        fig1 = portfolio_allocation_chart(metrics["holdings"])
        st.plotly_chart(fig1, use_container_width=True)

        st.markdown("### Sector Allocation")
        fig2 = sector_allocation_chart(metrics["sector_allocation"])
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("### Holdings Table")
        holdings_df = pd.DataFrame(metrics["holdings"])
        st.dataframe(holdings_df, use_container_width=True)


def market_tab():
    """
    Render the Market Explorer view.
    """
    st.subheader("Market Explorer")
    st.caption("Enter a ticker to review a simple market explanation and recent price trend.")

    ticker = st.text_input("Enter ticker symbol", value="AAPL", key="market_ticker")

    if st.button("Analyze Market", key="market_submit"):
        if not ticker.strip():
            st.warning("Please enter a ticker symbol.")
            return

        ticker = ticker.upper().strip()

        result = ask_market_question(
            user_query=f"What is happening with {ticker} right now?",
            ticker=ticker,
        )

        st.markdown("### Market Explanation")
        st.write(result["answer"])

        snapshot = result["market_data"]

        st.markdown("### Snapshot")
        st.json(snapshot)

        history_df = get_price_history(ticker, period="1mo", interval="1d")

        if not history_df.empty:
            st.markdown("### Price History")
            fig = price_history_chart(history_df, ticker)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No historical price data available.")


def main():
    config = load_config()

    st.set_page_config(
        page_title=config["ui"]["app_title"],
        layout="wide",
        initial_sidebar_state="expanded",
    )

    with st.sidebar:
        st.markdown("## Tools")

        selected_tool = st.radio(
            label="Choose a tool",
            options=[
                "Assistant",
                "Portfolio Explorer",
                "Market Explorer",
            ],
            index=0,
            label_visibility="collapsed",
        )

        st.divider()
        st.caption("For financial education only")
        st.caption("Not personalized financial advice")

        if st.button("Clear chat", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()

    render_sticky_header(config["ui"]["app_title"])

    if selected_tool == "Assistant":
        chat_tab()
    elif selected_tool == "Portfolio Explorer":
        portfolio_tab()
    elif selected_tool == "Market Explorer":
        market_tab()


main()