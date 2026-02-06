# state.py — Pause / resume handling

def pause_for_approval(site: str, vendor: str, cost: int, limit: int) -> dict:
    """
    Generate a pause state when cost exceeds approval limit.
    This is the human-in-the-loop checkpoint.

    Args:
        site:   Site name (e.g. "Pune")
        vendor: Selected vendor name
        cost:   Total cost of the order
        limit:  Site's approval limit

    Returns:
        A structured dict representing the paused state.
    """
    return {
        "status": "AWAITING_APPROVAL",
        "site": site,
        "selected_vendor": vendor,
        "amount": cost,
        "approval_limit": limit,
        "reason": f"Cost ₹{cost:,} exceeds site approval limit of ₹{limit:,}",
    }


def approve(paused_state: dict) -> dict:
    """Mark a paused state as approved. Ready for future resume logic."""
    return {
        **paused_state,
        "status": "APPROVED",
    }


def reject(paused_state: dict, reason: str = "Rejected by manager") -> dict:
    """Mark a paused state as rejected."""
    return {
        **paused_state,
        "status": "REJECTED",
        "rejection_reason": reason,
    }
