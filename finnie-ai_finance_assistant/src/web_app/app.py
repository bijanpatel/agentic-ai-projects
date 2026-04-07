import os
import sys
import streamlit as st
import pandas as pd
from src.utils.evaluation import log_interaction

# Add project root to Python path so `src.*` imports work when running Streamlit directly.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.core.config import load_config
from src.workflow.graph import build_workflow
from src.agents.portfolio_analysis_agent import ask_portfolio_question
from src.agents.market_analysis_agent import ask_market_question
from src.utils.portfolio import load_portfolio_data
from src.utils.market_data import get_price_history
from src.web_app.charts import (
    portfolio_allocation_chart,
    sector_allocation_chart,
    price_history_chart,
)


def render_sources(sources: list):
    """
    Render source references in the UI.

    Parameters:
        sources (list):
            A list of source dictionaries, usually containing:
            - title
            - source
    """
    if not sources:
        return

    st.markdown("**Sources**")
    for source in sources:
        st.write(f"- {source['title']} ({source['source']})")


def chat_tab():
    """
    Render the Chat Assistant tab.

    This tab uses the LangGraph workflow to route questions to:
    - Finance Q&A Agent
    - Tax Education Agent
    - Goal Planning Agent
    """
    st.subheader("Chat Assistant")
    st.write("Ask a finance education, tax education, or goal-planning question.")

    user_query = st.text_input("Ask a question", key="chat_input")

    if st.button("Submit Chat Question", key="chat_submit"):
        if not user_query.strip():
            st.warning("Please enter a question.")
            return

        app = build_workflow()
        result = app.invoke({"user_query": user_query})

        routed_agent = result.get("routed_agent", "unknown")
        agent_result = result.get("result", {})
        log_interaction({
            "user_query": user_query,
            "agent": agent_result.get("agent", routed_agent),
            "used_rag": agent_result.get("used_rag", False),
            "used_api": agent_result.get("used_api", False),
            "fallback_used": agent_result.get("fallback_used", False),
            "retrieved_doc_count": agent_result.get("retrieved_doc_count", 0),
        })

        st.markdown("### Answer")
        st.write(agent_result.get("answer", "No answer returned."))

        st.markdown("### Routed Agent")
        st.write(routed_agent)

        render_sources(agent_result.get("sources", []))


def portfolio_tab():
    """
    Render the Portfolio Analyzer tab.

    This tab:
    - loads sample portfolios
    - lets the user choose one
    - runs the portfolio analysis agent
    - displays explanation + charts
    """
    st.subheader("Portfolio Analyzer")
    st.write("Select a sample portfolio to analyze.")

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
        key="portfolio_select"
    )

    if st.button("Analyze Portfolio", key="portfolio_submit"):
        portfolio_id = portfolio_map[selected_label]

        result = ask_portfolio_question(
            user_query="Analyze this portfolio for a beginner investor.",
            portfolio_id=portfolio_id
        )

        st.markdown("### Portfolio Explanation")
        st.write(result["answer"])

        metrics = result["portfolio_metrics"]

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Value", f"${metrics['total_value']:,.2f}")
        col2.metric("Total Cost Basis", f"${metrics['total_cost_basis']:,.2f}")
        col3.metric("Unrealized Gain/Loss", f"${metrics['unrealized_gain_loss']:,.2f}")

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
    Render the Market Overview tab.

    This tab:
    - accepts a ticker symbol
    - runs the market analysis agent
    - fetches price history
    - shows explanation + chart + raw snapshot data
    """
    st.subheader("Market Overview")
    st.write("Enter a ticker symbol to get a simple market explanation.")

    ticker = st.text_input("Enter ticker symbol", value="AAPL", key="market_ticker")

    if st.button("Analyze Market", key="market_submit"):
        if not ticker.strip():
            st.warning("Please enter a ticker symbol.")
            return

        ticker = ticker.upper().strip()

        result = ask_market_question(
            user_query=f"What is happening with {ticker} right now?",
            ticker=ticker
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
    """
    Main entry point for the Streamlit app.

    This function:
    - loads configuration
    - sets page layout
    - renders tabs
    """
    config = load_config()

    st.set_page_config(
        page_title=config["ui"]["app_title"],
        layout="wide"
    )

    st.title(config["ui"]["app_title"])

    if config["ui"]["show_disclaimer"]:
        st.info(config["app"]["disclaimer"])

    tab1, tab2, tab3 = st.tabs(["Chat", "Portfolio", "Market"])

    with tab1:
        chat_tab()

    with tab2:
        portfolio_tab()

    with tab3:
        market_tab()


main()