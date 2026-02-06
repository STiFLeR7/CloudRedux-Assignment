# Intelligent Procurement Agent

A stateful, backend-only agent that assists Construction Site Managers with procurement decisions. Built with Google ADK + Gemini, but designed so the **LLM is a reasoning component, not a rule engine**.

---

## What This Agent Does

It has exactly **two jobs**:

1. **Remember rules** — persist site-specific policies (approval limits, banned vendors) to a JSON file
2. **Enforce them deterministically** — filter vendors, pick cheapest, pause if cost exceeds limits

The LLM (Gemini) only parses user intent and extracts fields. All business logic is pure Python.

---

## Architecture

```
┌─────────────────────────────────────────┐
│              Agent Layer                │
│   (Gemini via ADK — intent parsing)     │
├──────────┬──────────┬───────────────────┤
│  Memory  │  Tools   │      State        │
│  Layer   │  Layer   │      Layer        │
│          │          │                   │
│ JSON R/W │ Vendor   │ Pause/Resume      │
│          │ filter + │ for approval      │
│          │ cheapest │                   │
└──────────┴──────────┴───────────────────┘
```

| Layer | File | Responsibility |
|-------|------|----------------|
| Memory | `agent/memory.py` | Read/write site rules to `data/memory.json` |
| Tools | `agent/tools.py` | Load vendors, filter banned, select cheapest |
| State | `agent/state.py` | Generate `AWAITING_APPROVAL` pause state |
| Agent | `agent/agent.py` | ADK agent definition, tool registration |
| Entry | `main.py` | Two-turn scripted demo |

---

## Repository Structure

```
intelligent-procurement-agent/
├── agent/
│   ├── __init__.py        # Exports root_agent for ADK
│   ├── agent.py           # ADK agent orchestration
│   ├── memory.py          # Persistent rule storage (JSON)
│   ├── tools.py           # Deterministic vendor logic
│   └── state.py           # Pause / resume handling
├── data/
│   ├── memory.json        # Runtime rule store (starts empty)
│   └── mock_vendors.json  # Static vendor data (never changes)
├── docs/
│   └── work.txt           # Statement of Work
├── main.py                # CLI entry point
├── requirements.txt
├── .env                   # GOOGLE_API_KEY (not committed)
└── README.md
```

---

## How to Run

### Prerequisites

- Python 3.12+
- A Google API key ([get one here](https://aistudio.google.com/apikey))

### Setup

```bash
# Clone
git clone https://github.com/STiFLeR7/CloudRedux-Assignment.git
cd intelligent-procurement-agent

# Create venv & install
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

### Set your API key

Create a `.env` file in the project root:

```
GOOGLE_API_KEY=your-key-here
```

### Option 1: CLI Demo

```bash
python main.py
```

Runs two turns automatically:
- **Turn 1**: Stores Pune site rules (limit ₹40,000, bans BadRock Cements)
- **Turn 2**: Orders 100 bags of cement → selects GoodRock → pauses (cost exceeds limit)

### Option 2: ADK Web UI

```bash
adk web .
```

Open **http://localhost:8000/dev-ui/** in your browser. Select `agent` from the dropdown and chat interactively.

---

## Demo Walkthrough

### Turn 1 — Rule Ingestion

> **User**: "For the Pune site, the maximum approval limit is ₹40,000 and we strictly avoid 'BadRock Cements'."

**What happens**:
- Gemini extracts: site=Pune, limit=40000, banned=["BadRock Cements"]
- `store_site_rules()` writes to `data/memory.json`
- Rules persist across sessions

### Turn 2 — Procurement Order

> **User**: "Order 100 bags of cement for the Pune site."

**What happens** (all deterministic, no LLM):
1. Reads Pune rules from `memory.json`
2. Loads vendors from `mock_vendors.json`
3. Filters out BadRock Cements (banned) — even though it's cheapest at ₹35,000
4. Selects GoodRock (cheapest valid vendor @ ₹42,000)
5. ₹42,000 > ₹40,000 limit → returns `AWAITING_APPROVAL`

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| **JSON file for memory** | Intentionally visible I/O; no hidden state |
| **Deterministic vendor logic** | Business rules must not depend on LLM mood |
| **Pause as a state, not failure** | Models real enterprise approval workflows |
| **Gemini only parses intent** | LLM is a reasoning component, not a rule engine |
| **No extended context reliance** | Memory is architectural, not model-dependent |
| **Relative imports** | Clean package structure, works with ADK web |

### What the LLM does vs. doesn't do

| LLM Does | LLM Does NOT |
|----------|--------------|
| Parse "Pune site" from natural language | Decide which vendor to pick |
| Extract approval limit from text | Approve or reject orders |
| Understand "order cement" intent | Store or retrieve rules |
| Route to the correct tool | Calculate costs |

---

## Build Priority (how this was built)

- [x] **Memory** — `write_site_rules` / `read_site_rules` with JSON persistence
- [x] **Deterministic logic** — vendor filtering, cheapest selection, no AI
- [x] **Pause state** — `AWAITING_APPROVAL` with structured metadata
- [x] **Agent orchestration** — ADK Agent with two tool functions
- [x] **ADK integration** — `root_agent`, `adk web`, CLI runner
- [x] **Polish** — README, `.gitignore`, clean structure

---

## Testing

Run the CLI demo and verify:

| Scenario | Expected Outcome |
|----------|-----------------|
| Store Pune rules | `memory.json` contains approval_limit + banned_vendors |
| Order with banned vendor filtered | BadRock excluded, GoodRock selected |
| Cost exceeds limit | Status = `AWAITING_APPROVAL` |
| Cost within limit | Status = `APPROVED` |
| No rules set for site | Status = `ERROR` |
| All vendors banned | Status = `REJECTED` |

---

## Stack

- **Google ADK** (Agent Development Kit)
- **Gemini 2.0 Flash** via Google AI Studio
- **Python 3.12**
- **JSON** for persistent memory

---

## Closing Note

This implementation prioritizes **clarity, control, and correctness** over surface-level sophistication. The goal is not to show what the model can do, but to demonstrate how agentic systems should behave in real enterprise environments.
