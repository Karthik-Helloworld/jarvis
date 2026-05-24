"""
Memory store — saves and loads conversation history as JSON.
Keeps last 20 exchanges to avoid token bloat.
"""

import json
import os

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "history.json")
MAX_EXCHANGES = 20


def load_memory() -> list:
    """Load conversation history from disk."""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                history = json.load(f)
                if isinstance(history, list):
                    return history[-MAX_EXCHANGES * 2:]
        except Exception:
            pass
    return []


def save_memory(history: list):
    """Save conversation history to disk, trimmed to last N exchanges."""
    trimmed = history[-MAX_EXCHANGES * 2:]
    serializable = []
    for msg in trimmed:
        if isinstance(msg, dict):
            content = msg.get("content", "")
            if isinstance(content, str):
                serializable.append({"role": msg["role"], "content": content})
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(serializable, f, indent=2)
    except Exception as e:
        print(f"[Memory] Failed to save: {e}")


def clear_memory():
    """Wipe conversation history."""
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)
    print("[Memory] Cleared.")
