"""
Example 1: Two-Agent Debate
============================

Pattern: Peer-to-peer interaction
Agents:  Optimist ↔ Skeptic

Two agents take opposing positions on a topic and debate each other for
several rounds. This demonstrates:

  1. Creating agents with distinct personas
  2. Passing one agent's output as input to another
  3. Agents maintaining conversation context across turns

Run:
    python examples/01_two_agent_debate.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import anthropic
from dotenv import load_dotenv
from agents import Agent, Orchestrator

load_dotenv()


TOPIC = "AI will fundamentally improve human creativity rather than replace it"
ROUNDS = 3  # debate rounds


def build_agents(client: anthropic.Anthropic) -> tuple[Agent, Agent, Agent]:
    """Create the three agents for this example."""

    optimist = Agent(
        name="Optimist",
        system_prompt=(
            "You are an enthusiastic advocate who believes AI will augment and "
            "elevate human creativity. You support your arguments with concrete "
            "examples from art, music, writing, and science. Keep responses "
            "focused: 2-3 punchy paragraphs maximum."
        ),
        client=client,
        model="claude-haiku-4-5-20251001",
    )

    skeptic = Agent(
        name="Skeptic",
        system_prompt=(
            "You are a thoughtful critic who challenges optimistic claims about AI. "
            "You raise legitimate concerns about economic disruption, homogenization "
            "of creative output, and loss of human agency. Keep responses "
            "focused: 2-3 punchy paragraphs maximum."
        ),
        client=client,
        model="claude-haiku-4-5-20251001",
    )

    moderator = Agent(
        name="Moderator",
        system_prompt=(
            "You are an impartial debate moderator and intellectual synthesizer. "
            "Given a debate transcript, you identify the strongest points from "
            "each side, note areas of genuine disagreement, and offer a nuanced "
            "synthesis that honors both perspectives. Write in 3-4 paragraphs."
        ),
        client=client,
        model="claude-haiku-4-5-20251001",
    )

    return optimist, skeptic, moderator


def run_debate(client: anthropic.Anthropic) -> None:
    optimist, skeptic, moderator = build_agents(client)

    orch = Orchestrator(verbose=True)
    orch.register(optimist).register(skeptic).register(moderator)

    print("\n" + "=" * 60)
    print(f"DEBATE TOPIC: {TOPIC}")
    print("=" * 60)

    # --- Opening statements ---
    print("\n[OPENING STATEMENTS]")

    optimist_opening = orch.send(
        to="Optimist",
        message=(
            f"We are debating: '{TOPIC}'. "
            "Please give your opening argument in favor of this statement."
        ),
        from_name="Moderator",
    )

    skeptic_opening = orch.send(
        to="Skeptic",
        message=(
            f"We are debating: '{TOPIC}'. "
            "The Optimist just argued:\n\n"
            f"{optimist_opening}\n\n"
            "Please give your counter-argument."
        ),
        from_name="Moderator",
    )

    # --- Debate rounds ---
    current_optimist = optimist_opening
    current_skeptic = skeptic_opening

    for round_num in range(1, ROUNDS + 1):
        print(f"\n[ROUND {round_num}]")

        current_optimist = orch.send(
            to="Optimist",
            message=(
                f"The Skeptic responded:\n\n{current_skeptic}\n\n"
                "Rebut their points and strengthen your position."
            ),
            from_name="Skeptic",
        )

        current_skeptic = orch.send(
            to="Skeptic",
            message=(
                f"The Optimist responded:\n\n{current_optimist}\n\n"
                "Challenge their arguments and reinforce your concerns."
            ),
            from_name="Optimist",
        )

    # --- Moderator synthesis ---
    print("\n[MODERATOR SYNTHESIS]")

    debate_summary = (
        f"Debate topic: '{TOPIC}'\n\n"
        f"Optimist's final position:\n{current_optimist}\n\n"
        f"Skeptic's final position:\n{current_skeptic}"
    )

    orch.send(
        to="Moderator",
        message=(
            f"Here is a summary of the debate:\n\n{debate_summary}\n\n"
            "Please synthesize both perspectives into a balanced conclusion."
        ),
        from_name="System",
    )

    # --- Log ---
    orch.print_log()


if __name__ == "__main__":
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Set ANTHROPIC_API_KEY in your environment or .env file.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    run_debate(client)
