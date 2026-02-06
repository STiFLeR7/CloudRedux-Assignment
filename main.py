# main.py — Entry point
#
# Two-turn demo:
#   Turn 1: Store site rules (memory ingestion)
#   Turn 2: Process procurement order (reasoning & execution)

import asyncio
import os

from dotenv import load_dotenv
load_dotenv()  # Load GOOGLE_API_KEY from .env

from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from agent.agent import procurement_agent

# Vertex AI / Gemini API key — set via environment or .env
# export GOOGLE_API_KEY=your-key-here


async def call_agent(runner: Runner, user_id: str, session_id: str, message: str):
    """Send a message to the agent and print the final response."""
    print(f"\n>> USER: {message}")

    content = types.Content(
        role="user",
        parts=[types.Part(text=message)],
    )

    final_response = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    final_response += part.text

    print(f"<< AGENT: {final_response}")
    return final_response


async def main():
    session_service = InMemorySessionService()

    runner = Runner(
        agent=procurement_agent,
        app_name="intelligent_procurement_agent",
        session_service=session_service,
    )

    user_id = "site_manager_01"
    session_id = "session_001"

    # Create a session
    await session_service.create_session(
        app_name="intelligent_procurement_agent",
        user_id=user_id,
        session_id=session_id,
    )

    print("=" * 60)
    print("INTELLIGENT PROCUREMENT AGENT")
    print("=" * 60)

    # --- Turn 1: Rule ingestion ---
    print("\n--- TURN 1: Rule Ingestion ---")
    await call_agent(
        runner, user_id, session_id,
        "For the Pune site, the maximum approval limit is ₹40,000 "
        "and we strictly avoid 'BadRock Cements'."
    )

    # --- Turn 2: Procurement request ---
    print("\n--- TURN 2: Procurement Order ---")
    await call_agent(
        runner, user_id, session_id,
        "Order 100 bags of cement for the Pune site."
    )

    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
