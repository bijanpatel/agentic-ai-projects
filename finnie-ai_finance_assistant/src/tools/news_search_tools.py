from tavily import TavilyClient
from langchain.tools import tool

from src.core.config import load_config


def _search_tavily_news(query: str, max_results: int = 5) -> list[dict]:
    """
    Search finance/news results using Tavily.

    Returns:
        list[dict]:
            Normalized results.
    """
    config = load_config()
    api_key = config.get("tavily_api_key", "")

    if not api_key:
        return []

    try:
        client = TavilyClient(api_key=api_key)
        response = client.search(
            query=query,
            topic="finance",
            search_depth="basic",
            max_results=max_results,
        )
    except Exception as e:
        print("DEBUG Tavily request failed:", e)
        return []

    results = []
    for item in response.get("results", [])[:max_results]:
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "description": item.get("content", ""),
            "score": item.get("score", ""),
            "source": "Tavily Search",
        })

    return results


@tool
def search_finance_news_tool(query: str) -> str:
    """
    Search finance news using Tavily.

    Parameters:
        query (str):
            News query.

    Returns:
        str:
            Stringified list of normalized results.
    """
    results = _search_tavily_news(query=query, max_results=5)
    return str(results)