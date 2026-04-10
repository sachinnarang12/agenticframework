"""
Example 3: Research Team
=========================

Pattern: Parallel broadcast → sequential synthesis
Agents:  Researcher × 3 (parallel) → Analyst → Writer

Three specialist researchers explore different angles of a topic simultaneously.
Their findings are merged and handed to an Analyst who extracts key insights,
then a Writer produces a polished report.

This demonstrates:
  - Orchestrator.broadcast() — same prompt, multiple agents, parallel exploration
  - Collecting and merging responses from many agents
  - Multi-stage synthesis: raw research → insights → prose report

Run:
    python examples/03_research_team.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import anthropic
from dotenv import load_dotenv
from agents import Agent, Orchestrator

load_dotenv()

# ── change the topic to explore something else ────────────────────────────────
TOPIC = "the impact of large language models on software engineering workflows"
# ──────────────────────────────────────────────────────────────────────────────


def build_agents(client: anthropic.Anthropic) -> list[Agent]:
    tech_researcher = Agent(
        name="TechResearcher",
        system_prompt=(
            "You are a technical research specialist. Given a topic, you surface "
            "the most important technical facts, recent developments, tools, and "
            "architectural patterns. Focus on HOW things work. "
            "Use bullet points. Be specific, not generic."
        ),
        client=client,
        model="claude-opus-4-6",
    )

    impact_researcher = Agent(
        name="ImpactResearcher",
        system_prompt=(
            "You are a researcher specialising in societal and industry impact. "
            "Given a topic, you identify who is affected, how workflows/jobs "
            "change, real-world case studies, and quantitative data where possible. "
            "Focus on WHAT CHANGES for people. Use bullet points."
        ),
        client=client,
        model="claude-opus-4-6",
    )

    future_researcher = Agent(
        name="FutureResearcher",
        system_prompt=(
            "You are a foresight researcher. Given a topic, you identify emerging "
            "trends, open questions, predicted trajectories, and risks on a "
            "2-5 year horizon. Focus on WHAT'S NEXT. Use bullet points."
        ),
        client=client,
        model="claude-opus-4-6",
    )

    analyst = Agent(
        name="Analyst",
        system_prompt=(
            "You are a senior analyst. Given research notes from multiple "
            "perspectives, you distill the 5-7 most important cross-cutting "
            "insights. Each insight should synthesize multiple angles and be "
            "supported by evidence from the notes. Format: numbered list with "
            "a bold headline and 2-3 sentence explanation per insight."
        ),
        client=client,
        model="claude-opus-4-6",
    )

    writer = Agent(
        name="Writer",
        system_prompt=(
            "You are a technology journalist writing for an informed general "
            "audience. Given a list of key insights, you craft a well-structured "
            "report with: an engaging introduction, clearly titled sections "
            "(one per major insight), and a concise conclusion with a forward-looking "
            "statement. Aim for clarity and narrative flow over jargon."
        ),
        client=client,
        model="claude-opus-4-6",
    )

    return [tech_researcher, impact_researcher, future_researcher, analyst, writer]


def run_research_team(client: anthropic.Anthropic) -> None:
    agents = build_agents(client)

    orch = Orchestrator(verbose=True)
    for agent in agents:
        orch.register(agent)

    researchers = ["TechResearcher", "ImpactResearcher", "FutureResearcher"]

    print("\n" + "=" * 60)
    print(f"TOPIC: {TOPIC}")
    print("=" * 60)

    # ── Phase 1: Parallel research (each researcher explores a different angle) ─
    print("\n[Phase 1] Parallel research — 3 specialists explore the topic")

    research_prompt = (
        f"Research the following topic from your specialist perspective:\n\n"
        f"TOPIC: {TOPIC}\n\n"
        f"Provide detailed bullet-point findings."
    )

    all_findings: dict[str, str] = {}
    for name in researchers:
        print(f"\n  → Querying {name}…")
        all_findings[name] = orch.send(
            to=name,
            message=research_prompt,
            from_name="Orchestrator",
        )

    # ── Phase 2: Analyst synthesises all findings ─────────────────────────────
    print("\n[Phase 2] Analyst synthesises research into key insights")

    combined_research = "\n\n".join(
        f"=== {name} ===\n{findings}"
        for name, findings in all_findings.items()
    )

    insights = orch.send(
        to="Analyst",
        message=(
            f"Below are research notes from three specialists on the topic: "
            f"'{TOPIC}'\n\n"
            f"{combined_research}\n\n"
            f"Extract the 5-7 most important cross-cutting insights."
        ),
        from_name="ResearchTeam",
    )

    # ── Phase 3: Writer produces final report ─────────────────────────────────
    print("\n[Phase 3] Writer drafts the final report")

    orch.send(
        to="Writer",
        message=(
            f"Write a report on: '{TOPIC}'\n\n"
            f"Base it on these key insights from our research team:\n\n"
            f"{insights}"
        ),
        from_name="Analyst",
    )

    print("\n" + "=" * 60)
    print("RESEARCH TEAM COMPLETE — Report ready above.")
    print("=" * 60)

    orch.print_log()


if __name__ == "__main__":
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Set ANTHROPIC_API_KEY in your environment or .env file.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    run_research_team(client)
