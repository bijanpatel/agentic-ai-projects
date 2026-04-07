# Progress Demo Script — Week 1

## 1. Problem
This project addresses financial literacy challenges through a multi-agent AI finance assistant that explains concepts, supports goal planning, analyzes portfolios, and provides market context.

## 2. Why this architecture
The system uses:
- specialized agents for separation of concerns
- LangGraph for routing and stateful workflow
- RAG for grounded educational answers
- yFinance for live market context
- Streamlit for fast, interactive UI delivery

## 3. What is completed
- project setup and architecture
- curated finance knowledge base
- Chroma-based RAG pipeline
- Finance Q&A Agent
- Tax Education Agent
- Goal Planning Agent
- workflow routing with LangGraph
- Market Analysis Agent
- Portfolio Analysis Agent
- Streamlit app with chat, portfolio, and market tabs

## 4. Demo flow
- Ask: "What is an ETF?"
- Ask: "What is a Roth IRA?"
- Ask: "How should I build an emergency fund?"
- Show routed agent behavior
- Show Portfolio tab with sample portfolio
- Show Market tab with AAPL or VOO

## 5. What comes next
- test hardening
- documentation refinement
- deployment readiness
- final agent improvement milestone
- LLMOps / AgentOps and evaluation