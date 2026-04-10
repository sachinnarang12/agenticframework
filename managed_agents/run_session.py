"""
Managed Agents — RUNTIME Session Runner
=========================================

Run this script each time you want to execute the code-review pipeline on
Agent Core. It creates three sessions (one per agent), streams their events,
and passes output between agents exactly like the local examples — but now
each agent runs in Anthropic's hosted environment.

Prerequisites:
  1. Run managed_agents/setup.py first to create agents & environment.
  2. Copy the printed IDs into your .env file.

Usage:
  python managed_agents/run_session.py

Environment variables required (.env):
  ANTHROPIC_API_KEY
  AGENT_CORE_ENV_ID
  AGENT_ARCHITECT_ID / AGENT_ARCHITECT_VERSION
  AGENT_CODER_ID     / AGENT_CODER_VERSION
  AGENT_REVIEWER_ID  / AGENT_REVIEWER_VERSION

Pipeline:
  User task → Architect (design) → Coder (implement) → Reviewer (critique)
            → Coder (revise) → final code
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import anthropic
from dotenv import load_dotenv

load_dotenv()

# ── Change this to try different tasks ────────────────────────────────────────
TASK = "a rate-limited in-memory cache with TTL expiry and thread-safety in Python"
# ──────────────────────────────────────────────────────────────────────────────


def load_agent_ids() -> dict:
    """Load agent IDs from .env vars or the saved JSON file."""
    # Try environment variables first
    env_id = os.environ.get("AGENT_CORE_ENV_ID")
    architect_id = os.environ.get("AGENT_ARCHITECT_ID")
    architect_ver = os.environ.get("AGENT_ARCHITECT_VERSION")
    coder_id = os.environ.get("AGENT_CODER_ID")
    coder_ver = os.environ.get("AGENT_CODER_VERSION")
    reviewer_id = os.environ.get("AGENT_REVIEWER_ID")
    reviewer_ver = os.environ.get("AGENT_REVIEWER_VERSION")

    if all([env_id, architect_id, coder_id, reviewer_id]):
        return {
            "environment_id": env_id,
            "agents": {
                "Architect": {"id": architect_id, "version": int(architect_ver or 0)},
                "Coder":     {"id": coder_id,     "version": int(coder_ver or 0)},
                "Reviewer":  {"id": reviewer_id,  "version": int(reviewer_ver or 0)},
            },
        }

    # Fall back to JSON file written by setup.py
    json_path = os.path.join(os.path.dirname(__file__), "agent_ids.json")
    if os.path.exists(json_path):
        with open(json_path) as f:
            return json.load(f)

    print(
        "ERROR: Agent IDs not found.\n"
        "Run managed_agents/setup.py first and save the printed IDs to .env."
    )
    sys.exit(1)


def run_agent_session(
    client: anthropic.Anthropic,
    agent_id: str,
    agent_version: int,
    environment_id: str,
    user_message: str,
    agent_name: str,
) -> str:
    """
    Create a session for a single agent, send a message, stream the response,
    and return the agent's final text output.

    Args:
        client:         Anthropic client.
        agent_id:       The pre-created agent's ID.
        agent_version:  The agent version to pin to.
        environment_id: The shared environment ID.
        user_message:   The message to send.
        agent_name:     Display name (for logging).

    Returns:
        The agent's full text response.
    """
    print(f"\n{'─' * 60}")
    print(f"  Session: {agent_name}")
    print(f"{'─' * 60}")

    # Create a fresh session for this pipeline step
    session = client.beta.sessions.create(
        agent={"type": "agent", "id": agent_id, "version": agent_version},
        environment_id=environment_id,
        title=f"{agent_name} — pipeline step",
    )

    full_response = ""

    # Stream-first: open the stream, then send the message
    with client.beta.sessions.stream(session_id=session.id) as stream:
        client.beta.sessions.events.send(
            session_id=session.id,
            events=[{
                "type": "user.message",
                "content": [{"type": "text", "text": user_message}],
            }],
        )

        for event in stream:
            if event.type == "agent.message":
                for block in event.content:
                    if block.type == "text":
                        print(block.text, end="", flush=True)
                        full_response += block.text

            elif event.type == "session.status_idle":
                # Check stop reason — only break on terminal idle
                if event.stop_reason.type != "requires_action":
                    break

            elif event.type == "session.status_terminated":
                break

    print()  # newline after streamed output

    # Brief wait for status to settle before cleanup
    time.sleep(0.5)
    try:
        client.beta.sessions.archive(session_id=session.id)
    except Exception:
        pass  # non-fatal if archive fails

    return full_response


def run_pipeline(client: anthropic.Anthropic, ids: dict) -> None:
    env_id = ids["environment_id"]
    agents = ids["agents"]

    architect = agents["Architect"]
    coder     = agents["Coder"]
    reviewer  = agents["Reviewer"]

    print("\n" + "=" * 60)
    print(f"AGENT CORE PIPELINE")
    print(f"TASK: {TASK}")
    print("=" * 60)

    # ── Step 1: Architect designs ──────────────────────────────────────────────
    print("\n[Step 1/4] Architect")
    design = run_agent_session(
        client, architect["id"], architect["version"], env_id,
        user_message=f"Design a solution for: {TASK}",
        agent_name="Architect",
    )

    # ── Step 2: Coder implements ───────────────────────────────────────────────
    print("\n[Step 2/4] Coder — initial implementation")
    code = run_agent_session(
        client, coder["id"], coder["version"], env_id,
        user_message=f"Implement the following design as Python code:\n\n{design}",
        agent_name="Coder",
    )

    # ── Step 3: Reviewer reviews ───────────────────────────────────────────────
    print("\n[Step 3/4] Reviewer")
    review = run_agent_session(
        client, reviewer["id"], reviewer["version"], env_id,
        user_message=f"Review this Python code:\n\n{code}",
        agent_name="Reviewer",
    )

    # ── Step 4: Coder revises ─────────────────────────────────────────────────
    print("\n[Step 4/4] Coder — revision")
    final_code = run_agent_session(
        client, coder["id"], coder["version"], env_id,
        user_message=(
            "Here is a review of your code. Please produce a corrected version "
            "that addresses every issue raised.\n\n"
            f"REVIEW:\n{review}\n\n"
            f"ORIGINAL CODE:\n{code}"
        ),
        agent_name="Coder (revision)",
    )

    print("\n" + "=" * 60)
    print("AGENT CORE PIPELINE COMPLETE")
    print("=" * 60)
    print("\nFinal code is above (Step 4 output).")


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Set ANTHROPIC_API_KEY in your environment or .env file.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    ids = load_agent_ids()
    run_pipeline(client, ids)


if __name__ == "__main__":
    main()
