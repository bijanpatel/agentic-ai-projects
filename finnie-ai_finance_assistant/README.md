# FinanceAI : AI Finance Assistant

A multi-agent financial education assistant built for beginner users.  
The project combines a Streamlit interface, hybrid agent routing, retrieval-augmented generation (RAG), portfolio analysis, market context, financial news synthesis, basic guardrails, and lightweight agent-to-agent communication.

---

## Project Overview

Finnie AI Finance Assistant is designed to help users understand finance concepts in a simple and guided way. The system supports questions about investing basics, retirement and tax concepts, portfolio diversification, market analysis, and financial news. It uses a multi-agent workflow so different agents can handle different kinds of requests and optionally hand off work to one another when needed.

This project was built with a product-oriented mindset:
- a single Assistant experience for most interactions
- specialized tool views for portfolio and market exploration
- RAG-based grounding for finance education
- live or fallback news retrieval
- structured portfolio analysis from chat and CSV upload
- guardrails for safer and more relevant responses

---

## Key Features

- **Multi-agent architecture**
- **Hybrid routing** using rule-based logic plus LLM fallback
- **Finance Q&A** with retrieval-augmented generation
- **Tax education** support for retirement and investing-related tax basics
- **Goal-planning guidance** for time horizon, risk tolerance, and saving goals
- **Portfolio analysis** from:
  - chat-based holdings input
  - CSV upload in Portfolio Explorer
- **Market Explorer** for ticker-based market context
- **News Synthesizer** with live search plus curated fallback
- **Basic guardrails** for greetings, out-of-domain prompts, and risky advice requests
- **A2A-lite handoffs** between agents
- **Interaction logging** for lightweight LLMOps / AgentOps

---

## Architecture Overview

The system is organized into five main layers:

### 1. UI Layer
Built with **Streamlit**:
- Assistant
- Portfolio Explorer
- Market Explorer

### 2. Workflow Layer
Built with **LangGraph**:
- routing
- shared workflow state
- conditional handoffs
- final response orchestration

### 3. Agent Layer
Specialized agents handle different financial tasks:
- Finance Q&A Agent
- Tax Education Agent
- Goal Planning Agent
- Portfolio Analysis Agent
- Market Analysis Agent
- News Synthesizer Agent

### 4. Tool / Service Layer
External and internal tools support the agents:
- market snapshot and price history
- portfolio file parsing
- live news search
- curated fallback datasets

### 5. Knowledge Layer
A curated beginner finance knowledge base is indexed and used by the RAG-enabled finance agent.

---

## High-Level Workflow

```text
User Query
   ↓
Hybrid Router
   ↓
Primary Agent
   ↓
Optional Handoff (A2A-lite)
   ↓
Merged Final Response