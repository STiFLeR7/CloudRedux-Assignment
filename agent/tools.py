# tools.py — Vendor querying & utilities

import json
import os

VENDORS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "mock_vendors.json")


def load_vendors() -> list[dict]:
    """Load the static vendor list from disk."""
    with open(VENDORS_FILE, "r") as f:
        return json.load(f)


def filter_vendors(vendors: list[dict], banned: list[str]) -> list[dict]:
    """Remove banned vendors. Pure filter, no side effects."""
    banned_lower = [b.lower() for b in banned]
    return [v for v in vendors if v["name"].lower() not in banned_lower]


def select_cheapest(vendors: list[dict]) -> dict | None:
    """Pick the lowest-price vendor. Returns None if list is empty."""
    if not vendors:
        return None
    return min(vendors, key=lambda v: v["price"])


def evaluate_vendors(banned_vendors: list[str]) -> dict:
    """
    Full deterministic pipeline:
      1. Load vendors
      2. Filter out banned ones
      3. Select cheapest remaining

    Returns a dict with the result and metadata.
    """
    all_vendors = load_vendors()
    valid = filter_vendors(all_vendors, banned_vendors)
    cheapest = select_cheapest(valid)

    return {
        "all_vendors": all_vendors,
        "valid_vendors": valid,
        "selected": cheapest,
    }
