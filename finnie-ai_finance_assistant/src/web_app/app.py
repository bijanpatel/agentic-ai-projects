import os
import sys
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.core.config import load_config

def main():
    config = load_config()

    st.set_page_config(page_title=config["ui"]["app_title"], layout="wide")
    st.title(config["ui"]["app_title"])

    if config["ui"]["show_disclaimer"]:
        st.info(config["app"]["disclaimer"])

    st.write("Milestone 1 setup complete. UI foundation is ready.")

    tab1, tab2, tab3 = st.tabs(["Chat", "Portfolio", "Market"])

    with tab1:
        st.subheader("Chat Assistant")
        user_input = st.text_input("Ask a finance question")
        if user_input:
            st.write(f"You asked: {user_input}")

    with tab2:
        st.subheader("Portfolio Analyzer")
        st.write("Portfolio features will be added in later milestones.")

    with tab3:
        st.subheader("Market Overview")
        st.write("Market data features will be added in later milestones.")

main()