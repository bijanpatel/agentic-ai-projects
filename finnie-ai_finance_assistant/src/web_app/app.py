import os
import sys
import streamlit as st
import pandas as pd

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

# ─── Global CSS ─────────────────────────────────────────────────────────────

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
.block-container {
    padding-top: 0 !important;
    padding-bottom: 1rem !important;
    max-width: 100% !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 0.5px solid #e5e7eb !important;
    min-width: 230px !important;
    max-width: 230px !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }

/* Brand block */
.brand-block {
    display: flex; align-items: center; gap: 10px;
    padding: 20px 16px 16px;
    border-bottom: 0.5px solid #e5e7eb;
    margin-bottom: 12px;
}
.brand-icon {
    width: 34px; height: 34px; border-radius: 9px;
    background: #1D9E75;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; flex-shrink: 0;
}
.brand-name { font-size: 14px; font-weight: 600; color: #111; margin: 0; line-height: 1.2; }
.brand-sub  { font-size: 11px; color: #9ca3af; margin: 0; }

/* Nav label */
.nav-label {
    font-size: 10px; font-weight: 600; color: #b0b7c3;
    text-transform: uppercase; letter-spacing: 0.08em;
    margin: 4px 0 6px 16px;
}

/* Radio → nav-item style */
[data-testid="stSidebar"] .stRadio > label { display: none; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
    gap: 2px !important;
    padding: 0 12px !important;
}
[data-testid="stSidebar"] .stRadio label {
    display: flex !important;
    align-items: center !important;
    padding: 8px 10px !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    color: #6b7280 !important;
    cursor: pointer !important;
    width: 100% !important;
}
[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: #E1F5EE !important;
    color: #0F6E56 !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] .stRadio label input[type="radio"] { display: none !important; }

/* Sidebar clear button */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: 0.5px solid #e5e7eb !important;
    color: #6b7280 !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 8px 12px !important;
    width: 100% !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #f3f4f6 !important;
    color: #111 !important;
}

/* Disclaimer */
.disclaimer {
    font-size: 11px; color: #9ca3af; line-height: 1.5;
    background: #f9fafb; border-radius: 6px;
    padding: 9px 10px; border-left: 2px solid #1D9E75;
    margin: 0 12px;
}

/* ── Topbar ── */
.topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 13px 24px;
    background: #ffffff;
    border-bottom: 0.5px solid #e5e7eb;
    position: sticky; top: 0; z-index: 100;
}
.topbar-left { display: flex; align-items: center; gap: 8px; }
.topbar-title { font-size: 14px; font-weight: 500; color: #111; }
.status-dot { width: 7px; height: 7px; border-radius: 50%; background: #1D9E75; display: inline-block; }

/* ── Welcome block ── */
.welcome-wrap { text-align: center; padding: 28px 16px 8px; }
.welcome-icon-wrap {
    width: 48px; height: 48px; border-radius: 13px;
    background: #1D9E75;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 12px; font-size: 24px;
}
.welcome-title { font-size: 16px; font-weight: 500; color: #111; margin-bottom: 4px; }
.welcome-sub   { font-size: 13px; color: #6b7280; }

/* ── Quick prompt pills (st.button in columns) ── */
div[data-testid="stHorizontalBlock"] .stButton > button {
    font-size: 12px !important;
    padding: 6px 14px !important;
    border-radius: 20px !important;
    border: 0.5px solid #d1d5db !important;
    background: #fff !important;
    color: #6b7280 !important;
    font-family: 'DM Sans', sans-serif !important;
    width: 100% !important;
}
div[data-testid="stHorizontalBlock"] .stButton > button:hover {
    border-color: #1D9E75 !important;
    color: #0F6E56 !important;
    background: #E1F5EE !important;
}

/* ── Date divider ── */
.date-divider {
    display: flex; align-items: center; gap: 10px; margin: 12px 0;
}
.date-divider-line { flex: 1; height: 0.5px; background: #e5e7eb; }
.date-divider-text { font-size: 11px; color: #b0b7c3; }

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    border: none !important;
    background: transparent !important;
    padding: 2px 0 !important;
}

/* User bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stMarkdownContainer"] p {
    background: #1D9E75;
    color: white;
    border-radius: 12px 12px 4px 12px;
    padding: 10px 14px;
    font-size: 13px;
    line-height: 1.6;
    display: inline-block;
    max-width: 80%;
    margin-left: auto;
}

/* AI bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stMarkdownContainer"] p {
    background: #ffffff;
    border: 0.5px solid #e5e7eb;
    border-radius: 12px 12px 12px 4px;
    padding: 10px 14px;
    font-size: 13px;
    line-height: 1.6;
    color: #111;
    display: inline-block;
    max-width: 80%;
}

/* ── Chat input ── */
[data-testid="stChatInputContainer"] {
    border: 0.5px solid #d1d5db !important;
    border-radius: 12px !important;
    background: #f9fafb !important;
}
[data-testid="stChatInputContainer"]:focus-within { border-color: #1D9E75 !important; }
[data-testid="stChatInputContainer"] textarea {
    font-size: 13px !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stChatInputContainer"] button[kind="primaryFormSubmit"] {
    background: #1D9E75 !important;
    border-radius: 8px !important;
    border: none !important;
}
[data-testid="stChatInputContainer"] button[kind="primaryFormSubmit"]:hover {
    background: #0F6E56 !important;
}

/* Input hint */
.input-hint {
    font-size: 11px; color: #b0b7c3;
    text-align: center; padding: 6px 0 0;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: #f9fafb !important;
    border-radius: 10px !important;
    padding: 14px 16px !important;
    border: 0.5px solid #e5e7eb !important;
}
[data-testid="stMetricLabel"] { font-size: 12px !important; color: #9ca3af !important; }
[data-testid="stMetricValue"] { font-size: 22px !important; font-weight: 500 !important; color: #111 !important; }

/* Section titles */
.section-title { font-size: 18px; font-weight: 600; color: #111; margin-bottom: 4px; }
.section-sub   { font-size: 13px; color: #6b7280; margin-bottom: 20px; }

/* Info icon */
.info-icon { cursor: help; color: #9ca3af; font-size: 14px; line-height: 1; }
</style>
"""

# ─── Helper components ───────────────────────────────────────────────────────

def render_topbar(title: str):
    st.markdown(f"""
    <div class="topbar">
        <div class="topbar-left">
            <span class="status-dot"></span>
            <span class="topbar-title">{title}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_welcome():
    st.markdown("""
    <div class="welcome-wrap">
        <div class="welcome-icon-wrap">💰</div>
        <div class="welcome-title">How can I help you today?</div>
        <div class="welcome-sub">Ask about finance concepts, taxes, investing, or markets</div>
    </div>
    """, unsafe_allow_html=True)


def render_starter_prompts() -> str | None:
    """Render quick-action chips; returns selected prompt text or None."""
    prompts = [
        ("What is an ETF?",       "What is an ETF?"),
        ("Roth IRA basics",       "What is a Roth IRA?"),
        ("Analyze my portfolio",  "Analyze my portfolio"),
        ("Market news summary",   "Summarize recent market news for a beginner."),
    ]
    cols = st.columns(len(prompts))
    selected = None
    for col, (label, query) in zip(cols, prompts):
        with col:
            if st.button(label, key=f"qp_{label}", use_container_width=True):
                selected = query
    return selected


def render_date_divider(label: str = "Today"):
    st.markdown(f"""
    <div class="date-divider">
        <div class="date-divider-line"></div>
        <div class="date-divider-text">{label}</div>
        <div class="date-divider-line"></div>
    </div>
    """, unsafe_allow_html=True)


def render_response_details_icon(metadata: dict):
    if not metadata:
        return
    lines = [
        f"Agent: {metadata.get('routed_agent', 'unknown')}",
        f"Used RAG: {metadata.get('used_rag', False)}",
        f"Used API: {metadata.get('used_api', False)}",
        f"Fallback: {metadata.get('fallback_used', False)}",
    ]
    if metadata.get("needs_followup"):
        lines += [
            f"Needs Follow-up: {metadata['needs_followup']}",
            f"Follow-up Type: {metadata.get('followup_type', '')}",
        ]
    for src in metadata.get("sources", [])[:4]:
        lines.append(f"- {src['title']} ({src['source']})")

    tooltip = "&#10;".join(
        l.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")
        for l in lines
    )
    st.markdown(
        f'<div style="display:flex;justify-content:flex-end;margin-top:0.1rem;">'
        f'<span class="info-icon" title="{tooltip}">ⓘ</span></div>',
        unsafe_allow_html=True,
    )


# ─── Tab views ───────────────────────────────────────────────────────────────

def chat_tab():
    render_topbar("AI Finance Assistant")

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    starter_prompt = None
    if not st.session_state.chat_messages:
        render_welcome()
        starter_prompt = render_starter_prompts()
        render_date_divider()

    # Render conversation history
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                text_col, icon_col = st.columns([24, 1], vertical_alignment="top")
                with text_col:
                    st.write(msg["content"])
                with icon_col:
                    render_response_details_icon(msg.get("metadata", {}))
            else:
                st.write(msg["content"])

    # Chat input
    user_query = st.chat_input(
        "Ask about finance, tax, planning, portfolios, markets, or news"
    )
    st.markdown(
        '<div class="input-hint">For educational purposes only — not financial advice</div>',
        unsafe_allow_html=True,
    )

    final_query = user_query or starter_prompt
    if not final_query:
        return

    st.session_state.chat_messages.append({"role": "user", "content": final_query})

    app    = build_workflow()
    result = app.invoke({"user_query": final_query, "messages": st.session_state.chat_messages})

    routed_agent = result.get("routed_agent", "unknown")
    agent_result = result.get("result", {})
    answer       = agent_result.get("answer", "No answer returned.")

    metadata = {
        "routed_agent":        routed_agent,
        "used_rag":            agent_result.get("used_rag", False),
        "used_api":            agent_result.get("used_api", False),
        "fallback_used":       agent_result.get("fallback_used", False),
        "needs_followup":      result.get("needs_followup", False),
        "followup_type":       result.get("followup_type", ""),
        "sources":             agent_result.get("sources", []),
    }

    st.session_state.chat_messages.append({
        "role": "assistant", "content": answer, "metadata": metadata,
    })

    log_interaction({
        "user_query":          final_query,
        "agent":               agent_result.get("agent", routed_agent),
        "used_rag":            agent_result.get("used_rag", False),
        "used_api":            agent_result.get("used_api", False),
        "fallback_used":       agent_result.get("fallback_used", False),
        "retrieved_doc_count": agent_result.get("retrieved_doc_count", 0),
        "needs_followup":      result.get("needs_followup", False),
        "followup_type":       result.get("followup_type", ""),
    })

    st.rerun()


def portfolio_tab():
    render_topbar("Portfolio Explorer")
    st.markdown("""
    <div style="padding: 20px 24px 0;">
        <div class="section-title">Portfolio Explorer</div>
        <div class="section-sub">Choose a sample portfolio and review a beginner-friendly explanation.</div>
    </div>
    """, unsafe_allow_html=True)

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
        "Choose a portfolio", options=list(portfolio_map.keys()), key="portfolio_select"
    )

    if st.button("Analyze Portfolio", key="portfolio_submit"):
        portfolio_id = portfolio_map[selected_label]
        with st.spinner("Analyzing portfolio…"):
            result = ask_portfolio_question(
                user_query="Analyze this portfolio for a beginner investor.",
                portfolio_id=portfolio_id,
            )

        st.markdown("#### Portfolio explanation")
        st.write(result["answer"])

        metrics = result["portfolio_metrics"]
        col1, col2, col3 = st.columns(3)
        col1.metric("Total value",          f"${float(metrics['total_value']):,.2f}")
        col2.metric("Total cost basis",     f"${float(metrics['total_cost_basis']):,.2f}")
        col3.metric("Unrealized gain/loss", f"${float(metrics['unrealized_gain_loss']):,.2f}")

        st.markdown("#### Allocation by holding")
        st.plotly_chart(portfolio_allocation_chart(metrics["holdings"]),
                        use_container_width=True)

        st.markdown("#### Sector allocation")
        st.plotly_chart(sector_allocation_chart(metrics["sector_allocation"]),
                        use_container_width=True)

        st.markdown("#### Holdings table")
        st.dataframe(pd.DataFrame(metrics["holdings"]), use_container_width=True)


def market_tab():
    render_topbar("Market Explorer")
    st.markdown("""
    <div style="padding: 20px 24px 0;">
        <div class="section-title">Market Explorer</div>
        <div class="section-sub">Enter a ticker to see a plain-English explanation and recent price trend.</div>
    </div>
    """, unsafe_allow_html=True)

    ticker = st.text_input("Enter ticker symbol", value="AAPL", key="market_ticker")

    if st.button("Analyze Market", key="market_submit"):
        if not ticker.strip():
            st.warning("Please enter a ticker symbol.")
            return
        ticker = ticker.upper().strip()
        with st.spinner(f"Fetching data for {ticker}…"):
            result = ask_market_question(
                user_query=f"What is happening with {ticker} right now?",
                ticker=ticker,
            )

        st.markdown("#### Market explanation")
        st.write(result["answer"])

        st.markdown("#### Snapshot")
        st.json(result["market_data"])

        history_df = get_price_history(ticker, period="1mo", interval="1d")
        if not history_df.empty:
            st.markdown("#### Price history")
            st.plotly_chart(price_history_chart(history_df, ticker),
                            use_container_width=True)
        else:
            st.info("No historical price data available.")


# ─── Entry point ─────────────────────────────────────────────────────────────

def main():
    config = load_config()

    st.set_page_config(
        page_title=config["ui"]["app_title"],
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Inject global styles
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div class="brand-block">
            <div class="brand-icon">💰</div>
            <div>
                <div class="brand-name">FinanceAI</div>
                <div class="brand-sub">Education only</div>
            </div>
        </div>
        
        """, unsafe_allow_html=True)

        selected_tool = st.radio(
            label="Tool",
            options=["Assistant", "Portfolio Explorer", "Market Explorer"],
            index=0,
            label_visibility="collapsed",
        )

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="disclaimer">
            For financial education only.<br>
            Not personalized financial advice.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        if "Assistant" in selected_tool:
            if st.button("Clear chat", use_container_width=True):
                st.session_state.chat_messages = []
                st.rerun()

    # ── Main content ─────────────────────────────────────────────────────────
    if "Assistant" in selected_tool:
        chat_tab()
    elif "Portfolio" in selected_tool:
        portfolio_tab()
    else:
        market_tab()


main()