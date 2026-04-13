"""
Example 2: Code Review Pipeline
=================================

Pattern: Sequential pipeline
Agents:  Architect → Coder → Reviewer → (Coder revises)

A user request flows through a chain of specialist agents, each adding value:
  1. Architect  — breaks the request into a clear design plan
  2. Coder      — implements the plan as working Python code
  3. Reviewer   — finds bugs, style issues, and security concerns
  4. Coder      — revises the code based on reviewer feedback

This demonstrates:
  - Orchestrator.pipeline() for chained execution
  - How each agent's output becomes the next agent's input
  - A revision loop (Coder sees Reviewer feedback)

Run:
    python examples/02_code_pipeline.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import anthropic
from dotenv import load_dotenv
from agents import Agent, Orchestrator

load_dotenv()

# ── change this to try different tasks ────────────────────────────────────────
TASK = "a rate-limited in-memory cache with TTL expiry and thread-safety in Python"
# ──────────────────────────────────────────────────────────────────────────────


def build_agents(client: anthropic.Anthropic) -> dict[str, Agent]:
    architect = Agent(
        name="Architect",
        system_prompt=(
            "You are a senior software architect. Given a feature request, you "
            "produce a concise technical design: data structures, class/function "
            "signatures, edge cases to handle, and a brief rationale. "
            "Do NOT write full implementation code — only the blueprint. "
            "Format your output with clear headings."
        ),
        client=client,
        model="claude-haiku-4-5-20251001",
    )

    coder = Agent(
        name="Coder",
        system_prompt=(
            "You are an expert Python developer. Given a design plan, you write "
            "clean, idiomatic, production-quality Python code. "
            "Include docstrings, type hints, and a usage example at the bottom. "
            "Output ONLY the code block — no prose before or after."
        ),
        client=client,
        model="claude-haiku-4-5-20251001",
    )

    reviewer = Agent(
        name="Reviewer",
        system_prompt=(
            "You are a meticulous code reviewer. Given Python code, you identify:\n"
            "  • Correctness issues or bugs\n"
            "  • Missing edge-case handling\n"
            "  • Style / PEP-8 violations\n"
            "  • Security concerns\n"
            "  • Performance problems\n"
            "Format your review as a numbered list of issues. "
            "Be specific: quote the relevant line(s) and explain the fix."
        ),
        client=client,
        model="claude-haiku-4-5-20251001",
    )

    return {"Architect": architect, "Coder": coder, "Reviewer": reviewer}


def run_pipeline(client: anthropic.Anthropic) -> None:
    agents = build_agents(client)

    orch = Orchestrator(verbose=True)
    for agent in agents.values():
        orch.register(agent)

    print("\n" + "=" * 60)
    print(f"TASK: Build {TASK}")
    print("=" * 60)

    # ── Step 1: Architect designs ──────────────────────────────────────────────
    print("\n[Step 1/4] Architect designs the solution")
    design = orch.send(
        to="Architect",
        message=f"Design a solution for: {TASK}",
        from_name="User",
    )

    # ── Step 2: Coder implements ───────────────────────────────────────────────
    print("\n[Step 2/4] Coder implements the design")
    code = orch.send(
        to="Coder",
        message=(
            f"Implement the following design as Python code:\n\n{design}"
        ),
        from_name="Architect",
    )

    # ── Step 3: Reviewer reviews ───────────────────────────────────────────────
    print("\n[Step 3/4] Reviewer reviews the code")
    review = orch.send(
        to="Reviewer",
        message=f"Review this Python code:\n\n{code}",
        from_name="Coder",
    )

    # ── Step 4: Coder revises based on feedback ────────────────────────────────
    print("\n[Step 4/4] Coder revises based on review feedback")
    final_code = orch.send(
        to="Coder",
        message=(
            "Here is a review of your code. Please produce a corrected version "
            "that addresses every issue raised.\n\n"
            f"REVIEW:\n{review}\n\n"
            f"ORIGINAL CODE:\n{code}"
        ),
        from_name="Reviewer",
    )

    # ── Summary ────────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE — Final code ready above.")
    print("=" * 60)

    orch.print_log()


if __name__ == "__main__":
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Set ANTHROPIC_API_KEY in your environment or .env file.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    run_pipeline(client)
