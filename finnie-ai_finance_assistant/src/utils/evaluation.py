import json
from pathlib import Path
from datetime import datetime


def log_interaction(record: dict, log_file: str = "logs/eval_log.jsonl"):
    """
    Append one evaluation/interaction record to a JSONL log file.

    Parameters:
        record (dict):
            Structured record describing the interaction.
            Example fields:
            - user_query
            - agent
            - used_rag
            - used_api
            - fallback_used
            - retrieved_doc_count

        log_file (str):
            Path to the JSONL log file.

    Why this matters:
        This is a lightweight step toward LLMOps / AgentOps.
        It lets us inspect behavior over time without adding heavy infrastructure.
    """
    path = Path(log_file)
    path.parent.mkdir(parents=True, exist_ok=True)

    enriched_record = {
        "timestamp": datetime.utcnow().isoformat(),
        **record,
    }

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(enriched_record) + "\n")