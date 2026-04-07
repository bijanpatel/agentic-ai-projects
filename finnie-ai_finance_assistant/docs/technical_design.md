# Technical Design — AI Finance Assistant

## 1. Problem Statement
The AI Finance Assistant is designed to improve financial literacy by providing beginner-friendly financial education through a multi-agent conversational interface.

## 2. Core Architecture
The application uses:
- OpenAI for language generation
- LangGraph for workflow orchestration
- Chroma for vector storage
- Streamlit for UI
- yFinance for market data
- Pandas/Plotly for analysis and visualization

## 3. Agent Design
Implemented agents:
- Finance Q&A Agent
- Tax Education Agent
- Goal Planning Agent
- Market Analysis Agent
- Portfolio Analysis Agent

Planned later:
- News Synthesizer Agent refinement
- cross-agent improvement milestone

## 4. Workflow Design
Current workflow:
- user query enters Streamlit
- LangGraph router selects a target agent
- selected agent executes
- response is returned to UI

## 5. RAG Design
The knowledge base is stored in JSONL format.
Documents are:
- loaded
- chunked
- embedded
- stored in Chroma
- retrieved with similarity threshold logic

## 6. Portfolio Analysis Design
Portfolio analysis is based on structured sample portfolio data and deterministic calculations:
- holding value
- cost basis
- unrealized gain/loss
- allocation percentage
- sector allocation
- asset type allocation

## 7. Market Data Design
Market data is fetched from yFinance for:
- ticker snapshot
- historical price data

## 8. Safety and Trust
The system is designed for financial education, not personalized advice.
Responses avoid direct buy/sell recommendations and use disclaimers where relevant.

## 9. Future Improvements
- stronger fallback routing
- better ticker extraction
- portfolio enrichment with live prices
- broader evaluation
- AWS deployment
- LLMOps / AgentOps metrics