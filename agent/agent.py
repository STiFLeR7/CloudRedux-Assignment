# agent.py — ADK agent orchestration
#
# Gemini's ONLY jobs here:
#   1. Parse user intent (rule ingestion vs. procurement request)
#   2. Extract structured fields (site name, limits, banned vendors, item, quantity)
#
# Everything else is deterministic Python:
#   - memory.py stores/retrieves rules
#   - tools.py filters vendors and picks cheapest
#   - state.py pauses execution when limits are exceeded

from google.adk.agents import Agent

from .memory import write_site_rules, read_site_rules
from .tools import evaluate_vendors
from .state import pause_for_approval


# ---------------------------------------------------------------------------
#  Tool functions exposed to the ADK agent
#  (Gemini calls these; the logic inside is pure Python)
# ---------------------------------------------------------------------------

def store_site_rules(site: str, approval_limit: int, banned_vendors: list[str]) -> dict:
    """
    Store procurement rules for a construction site.
    Call this when the user provides rules like approval limits or banned vendors.

    Args:
        site: The site name (e.g. "Pune").
        approval_limit: Maximum amount (in ₹) that can be auto-approved.
        banned_vendors: List of vendor names that are not allowed.

    Returns:
        Confirmation of stored rules.
    """
    rules = {
        "approval_limit": approval_limit,
        "banned_vendors": banned_vendors,
    }
    stored = write_site_rules(site, rules)
    return {"status": "RULES_STORED", "site": site, "rules": stored}


def process_procurement(site: str, item: str, quantity: int) -> dict:
    """
    Process a procurement order for a construction site.
    Call this when the user wants to order materials.

    Args:
        site: The site name (e.g. "Pune").
        item: The material to procure (e.g. "cement").
        quantity: Number of units to order.

    Returns:
        The procurement decision: approved, paused for approval, or rejected.
    """
    # 1. Retrieve stored rules
    rules = read_site_rules(site)
    if rules is None:
        return {
            "status": "ERROR",
            "reason": f"No rules found for site '{site}'. Please set up site rules first.",
        }

    approval_limit = rules["approval_limit"]
    banned_vendors = rules.get("banned_vendors", [])

    # 2. Deterministic vendor evaluation
    result = evaluate_vendors(banned_vendors)
    selected = result["selected"]

    if selected is None:
        return {
            "status": "REJECTED",
            "reason": "All vendors are banned. No valid vendor available.",
            "banned_vendors": banned_vendors,
        }

    total_cost = selected["price"]

    # 3. Apply approval logic
    if total_cost <= approval_limit:
        return {
            "status": "APPROVED",
            "site": site,
            "item": item,
            "quantity": quantity,
            "selected_vendor": selected["name"],
            "total_cost": total_cost,
            "approval_limit": approval_limit,
            "reason": f"Cost ₹{total_cost:,} is within approval limit of ₹{approval_limit:,}",
        }
    else:
        return pause_for_approval(
            site=site,
            vendor=selected["name"],
            cost=total_cost,
            limit=approval_limit,
        )


# ---------------------------------------------------------------------------
#  ADK Agent definition
# ---------------------------------------------------------------------------

procurement_agent = Agent(
    name="procurement_agent",
    model="gemini-2.0-flash",
    description="Intelligent procurement agent for construction site management.",
    instruction="""You are a procurement assistant for construction site managers.

You have exactly TWO jobs:

1. REMEMBER RULES — When the user tells you about site rules (approval limits,
   banned vendors), call the store_site_rules tool to persist them.

2. ENFORCE RULES — When the user asks to order/procure materials, call the
   process_procurement tool. Report the result exactly as returned.

IMPORTANT:
- Do NOT make up vendor names or prices. The tools handle that.
- Do NOT approve or reject orders yourself. The tools decide.
- Do NOT skip calling tools. Every user message needs exactly one tool call.
- Parse the user's message to extract: site name, approval limit, banned vendors,
  item name, and quantity. Pass them to the appropriate tool.
""",
    tools=[store_site_rules, process_procurement],
)

# ADK web discovers this variable by convention
root_agent = procurement_agent
