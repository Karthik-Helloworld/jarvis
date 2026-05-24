"""
Web search skill — uses DuckDuckGo Instant Answer API (free, no key needed).
Falls back to a simple scrape summary if instant answer is empty.
"""

import urllib.request
import urllib.parse
import json


def web_search(query: str) -> str:
    """Search the web and return a concise answer."""
    try:
        encoded = urllib.parse.quote(query)
        url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1&skip_disambig=1"

        req = urllib.request.Request(url, headers={"User-Agent": "JARVIS/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())

        abstract = data.get("AbstractText", "").strip()
        if abstract:
            source = data.get("AbstractSource", "")
            return f"{abstract[:400]} (Source: {source})"

        answer = data.get("Answer", "").strip()
        if answer:
            return answer

        related = data.get("RelatedTopics", [])
        if related:
            summaries = []
            for item in related[:3]:
                if isinstance(item, dict) and item.get("Text"):
                    summaries.append(item["Text"][:120])
            if summaries:
                return " | ".join(summaries)

        return f"No direct answer found for '{query}'. Try rephrasing or ask me to be more specific."

    except Exception as e:
        return f"Search failed: {str(e)}"
