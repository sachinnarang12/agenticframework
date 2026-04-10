"""
Managed Agents — ONE-TIME SETUP
================================

Run this script ONCE to create the long-lived Agent objects and a shared
Environment on Anthropic's Agent Core platform. Save the printed IDs to
your .env file — they are reused every time you run a session.

Prerequisites:
  pip install anthropic python-dotenv
  export ANTHROPIC_API_KEY=...

Usage:
  python managed_agents/setup.py

What it creates:
  - 1 Environment  (the sandbox container template)
  - 3 Agents       (Architect, Coder, Reviewer) — each is a versioned config
  - Prints agent + environment IDs to paste into .env

IMPORTANT: Do NOT re-run this every time you want a pipeline. Create agents
once, then reference them by ID in run_session.py.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import anthropic
from dotenv import load_dotenv

load_dotenv()


def create_environment(client: anthropic.Anthropic) -> str:
    """Create a reusable cloud environment for agent sessions."""
    print("Creating environment…")
    env = client.beta.environments.create(
        name="agenticframework-env",
        config={
            "type": "cloud",
            "networking": {"type": "unrestricted"},
        },
    )
    print(f"  ✓ Environment created: {env.id}")
    return env.id


def create_agents(client: anthropic.Anthropic) -> dict[str, dict]:
    """Create the three specialist agents on Agent Core."""

    agent_configs = [
        {
            "name": "Architect",
            "description": "Designs software solutions from requirements",
            "system": (
                "You are a senior software architect. Given a feature request, "
                "produce a concise technical design: data structures, class/function "
                "signatures, edge cases to handle, and a brief rationale. "
                "Do NOT write full implementation code — only the blueprint. "
                "Format your output with clear headings."
            ),
            "tools": [{"type": "agent_toolset_20260401"}],
        },
        {
            "name": "Coder",
            "description": "Implements designs as clean Python code",
            "system": (
                "You are an expert Python developer. Given a design plan, write "
                "clean, idiomatic, production-quality Python code. "
                "Include docstrings, type hints, and a usage example at the bottom. "
                "Output ONLY the code block — no prose before or after."
            ),
            "tools": [{"type": "agent_toolset_20260401"}],
        },
        {
            "name": "Reviewer",
            "description": "Reviews code for bugs, style, and security issues",
            "system": (
                "You are a meticulous code reviewer. Given Python code, identify:\n"
                "  • Correctness issues or bugs\n"
                "  • Missing edge-case handling\n"
                "  • Style / PEP-8 violations\n"
                "  • Security concerns\n"
                "  • Performance problems\n"
                "Format your review as a numbered list. Be specific: quote the "
                "relevant line(s) and explain the fix."
            ),
            "tools": [{"type": "agent_toolset_20260401"}],
        },
    ]

    created: dict[str, dict] = {}

    for cfg in agent_configs:
        print(f"Creating agent: {cfg['name']}…")
        agent = client.beta.agents.create(
            name=cfg["name"],
            description=cfg["description"],
            model="claude-opus-4-6",
            system=cfg["system"],
            tools=cfg["tools"],
        )
        created[cfg["name"]] = {"id": agent.id, "version": agent.version}
        print(f"  ✓ Agent '{cfg['name']}': id={agent.id}  version={agent.version}")

    return created


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Set ANTHROPIC_API_KEY in your environment or .env file.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    print("\n" + "=" * 60)
    print("AGENT CORE — One-time Setup")
    print("=" * 60 + "\n")

    env_id = create_environment(client)
    agents = create_agents(client)

    # ── Print .env snippet ─────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("Setup complete! Add the following to your .env file:")
    print("=" * 60)
    print(f"\nAGENT_CORE_ENV_ID={env_id}")
    for name, info in agents.items():
        key = name.upper()
        print(f"AGENT_{key}_ID={info['id']}")
        print(f"AGENT_{key}_VERSION={info['version']}")

    # Also save to a JSON file for reference
    output = {
        "environment_id": env_id,
        "agents": agents,
    }
    out_path = os.path.join(os.path.dirname(__file__), "agent_ids.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nAlso saved to: {out_path}")
    print()


if __name__ == "__main__":
    main()
