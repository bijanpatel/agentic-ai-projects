# Evaluation Plan — AI Finance Assistant

## 1. Routing Accuracy
Evaluate whether the LangGraph router sends the query to the correct agent.

Artifacts:
- `src/data/eval/routing_eval_set.json`
- `tests/test_router.py`

## 2. Retrieval Quality
Evaluate whether in-domain finance queries retrieve relevant finance KB documents.

Artifacts:
- `tests/test_rag_basic.py`
- manual retrieval checks

## 3. Answer Quality
Evaluate responses for:
- clarity
- correctness
- beginner-friendliness
- source grounding
- safety framing

## 4. Tool Usage Quality
Evaluate:
- market snapshot retrieval
- price-history retrieval
- portfolio metric calculations

## 5. Fallback Safety
Evaluate whether the system responds safely when:
- retrieval is weak
- query is out-of-domain
- ticker is invalid
- data is missing

## 6. Logging and Observability
Interaction logs are stored in:
- `logs/eval_log.jsonl`

These can be reviewed to inspect:
- chosen agent
- retrieval count
- fallback usage
- API usage