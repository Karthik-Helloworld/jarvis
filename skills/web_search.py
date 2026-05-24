"""
Web search skill — uses Tavily API for real-time accurate results.
Free tier: 1,000 searches/month.
"""

import os
from tavily import TavilyClient


def web_search(query: str) -> str:
    """Search the web and return a concise answer."""
    try:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return "Tavily API key not set in .env file."

        client = TavilyClient(api_key=api_key)
        response = client.search(
            query=query,
            search_depth="basic",
            max_results=3,
            include_answer=True
        )

        if response.get("answer"):
            return response["answer"]

        results = response.get("results", [])
        if results:
            summaries = []
            for r in results[:3]:
                title = r.get("title", "")
                content = r.get("content", "")[:150]
                summaries.append(f"{title}: {content}")
            return " | ".join(summaries)

        return f"No results found for '{query}'."

    except Exception as e:
        return f"Search failed: {str(e)}"
