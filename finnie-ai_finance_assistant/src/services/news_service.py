import ast
import json
from pathlib import Path

from src.tools.news_search_tools import search_finance_news_tool


def load_sample_news() -> list[dict]:
    """
    Load fallback sample news dataset.
    """
    path = Path("src/data/news/sample_finance_news.json")
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_news_context(query: str) -> tuple[list[dict], str]:
    """
    Try live search first; fall back to sample dataset.

    Returns:
        tuple:
            (news_items, source_mode)
            source_mode in {"live_search", "fallback_sample"}
    """
    try:
        raw_results = search_finance_news_tool.invoke({"query": query})
        live_results = ast.literal_eval(raw_results) if raw_results else []
    except Exception:
        live_results = []

    if live_results:
        normalized = []
        for i, item in enumerate(live_results, start=1):
            normalized.append({
                "news_id": f"live_{i}",
                "title": item.get("title", ""),
                "source": item.get("source", "Brave Search"),
                "published_at": item.get("age", ""),
                "category": "live_search",
                "summary": item.get("description", ""),
                "key_points": [],
                "why_it_matters": "",
                "url": item.get("url", ""),
            })
        return normalized, "live_search"

    return load_sample_news(), "fallback_sample"