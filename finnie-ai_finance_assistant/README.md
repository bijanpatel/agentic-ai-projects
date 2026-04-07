# AI Finance Assistant

## Overview
AI Finance Assistant is a multi-agent financial education application built with OpenAI, LangGraph, Chroma, Streamlit, and yFinance. It helps users learn finance concepts, understand tax basics, explore financial goals, analyze sample portfolios, and view market data in a beginner-friendly way.

## Features
- Multi-agent workflow using LangGraph
- Finance Q&A Agent
- Tax Education Agent
- Goal Planning Agent
- Portfolio Analysis Agent
- Market Analysis Agent
- RAG over a curated finance knowledge base
- Streamlit-based UI with chat, portfolio, and market tabs
- Portfolio visualizations and price-history charts

## Architecture
Main components:
- `src/agents/` — specialized agents
- `src/workflow/` — routing and LangGraph workflow
- `src/rag/` — embeddings, vector store, retrieval
- `src/utils/` — market and portfolio utilities
- `src/web_app/` — Streamlit UI
- `src/data/` — knowledge base, portfolios, evaluation datasets

## Project Structure
```text
ai_finance_assistant/
├── src/
│   ├── agents/
│   ├── core/
│   ├── data/
│   ├── rag/
│   ├── utils/
│   ├── web_app/
│   └── workflow/
├── tests/
├── docs/
├── config.yaml
├── requirements.txt
├── README.md
└── run.py