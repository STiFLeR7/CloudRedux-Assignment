# memory.py — Persistent rule storage

import json
import os

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "memory.json")


def _load_memory() -> dict:
    """Load the entire memory store from disk."""
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def _save_memory(data: dict) -> None:
    """Write the entire memory store to disk."""
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def write_site_rules(site: str, rules: dict) -> dict:
    """
    Persist rules for a given site.

    Args:
        site:  Site name (e.g. "Pune").
        rules: Dict with keys like "approval_limit", "banned_vendors".

    Returns:
        The stored rules for confirmation.
    """
    memory = _load_memory()
    memory[site] = rules
    _save_memory(memory)
    return memory[site]


def read_site_rules(site: str) -> dict | None:
    """
    Retrieve stored rules for a site.

    Args:
        site: Site name.

    Returns:
        The rules dict, or None if the site has no rules.
    """
    memory = _load_memory()
    return memory.get(site)
