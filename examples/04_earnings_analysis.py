"""
Example 4: Earnings Analysis — Asset Management
================================================

Pattern: Sequential pipeline with financial domain agents
Agents:  Researcher → Bull Analyst → Bear Analyst → Risk Manager → Report Writer

A practical asset management pipeline that takes an earnings call transcript
(or company description) and produces a full investment memo through five
specialist agents that challenge each other's reasoning.

This demonstrates:
  - Domain-specific system prompts for finance
  - Bull vs Bear debate pattern (challenge mechanism)
  - Risk management layer before the final output
  - Downloadable investment memo

Run:
    python examples/04_earnings_analysis.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import anthropic
from dotenv import load_dotenv
from agents import Agent, Orchestrator

load_dotenv()

# ── Paste your transcript here, or use this sample ────────────────────────────
COMPANY = "Apple"
TRANSCRIPT = """
Apple Q4 FY2024 Earnings Summary:
- Revenue: $94.9B (+6% YoY), beat estimates of $94.3B
- EPS: $1.64, beat estimates of $1.60
- iPhone revenue: $46.2B (+6% YoY) — stronger than expected
- Services revenue: $24.9B (+12% YoY) — record high
- Mac revenue: $7.7B (+2% YoY)
- iPad revenue: $7.0B (+8% YoY)
- Wearables: $9.0B (-3% YoY)
- Gross margin: 46.2% (record high)
- Cash & equivalents: $156B
- Share buybacks: $25B in the quarter
- Q1 FY2025 guidance: low to mid single digit revenue growth
- CEO Tim Cook: "We're incredibly excited about our AI roadmap with Apple Intelligence"
- CFO: Services margin continues to expand, targeting 50%+ long-term
- China revenue: $15B (-1% YoY), competition from Huawei mentioned
"""
# ──────────────────────────────────────────────────────────────────────────────


def build_agents(client: anthropic.Anthropic) -> dict[str, Agent]:
    return {
        "Researcher": Agent(
            name="Researcher",
            system_prompt=(
                "You are a financial research analyst. Given an earnings transcript, "
                "extract and organise:\n"
                "  • Revenue, earnings, margins (actuals vs expectations)\n"
                "  • Management guidance and outlook\n"
                "  • Key business segment performance\n"
                "  • Notable quotes from management\n"
                "  • Any surprises (positive or negative)\n"
                "Use bullet points. Be specific with numbers."
            ),
            client=client,
            model="claude-opus-4-6",
        ),
        "BullAnalyst": Agent(
            name="BullAnalyst",
            system_prompt=(
                "You are a bullish equity analyst. Build the strongest possible "
                "investment case FOR buying this stock. Cover: growth catalysts, "
                "competitive moat, valuation support, management quality. "
                "Use bullet points with specific evidence from the data."
            ),
            client=client,
            model="claude-opus-4-6",
        ),
        "BearAnalyst": Agent(
            name="BearAnalyst",
            system_prompt=(
                "You are a bearish equity analyst. Build the strongest possible "
                "case AGAINST this stock. Cover: risks, decelerating growth, "
                "competition, valuation concerns, red flags in management commentary. "
                "Use bullet points with specific evidence."
            ),
            client=client,
            model="claude-opus-4-6",
        ),
        "RiskManager": Agent(
            name="RiskManager",
            system_prompt=(
                "You are a portfolio risk manager. Given bull and bear cases, "
                "identify the top 5 risks that could invalidate the bull thesis. "
                "For each risk: assign likelihood (Low/Medium/High), "
                "potential impact (Low/Medium/High), and suggest how to monitor "
                "or hedge it."
            ),
            client=client,
            model="claude-opus-4-6",
        ),
        "ReportWriter": Agent(
            name="ReportWriter",
            system_prompt=(
                "You are a senior portfolio manager writing an investment memo. "
                "Structure your memo as:\n"
                "  1. Executive Summary (Buy/Hold/Sell + 1-sentence rationale)\n"
                "  2. Key Facts\n"
                "  3. Bull Case\n"
                "  4. Bear Case\n"
                "  5. Key Risks\n"
                "  6. Recommendation & Position Sizing\n"
                "Be concise, direct, and actionable."
            ),
            client=client,
            model="claude-opus-4-6",
        ),
    }


def run_earnings_analysis(client: anthropic.Anthropic) -> None:
    agents = build_agents(client)

    orch = Orchestrator(verbose=True)
    for agent in agents.values():
        orch.register(agent)

    print("\n" + "=" * 60)
    print(f"EARNINGS ANALYSIS: {COMPANY}")
    print("=" * 60)

    # Step 1 — Researcher extracts facts
    print("\n[Step 1/5] Researcher — extracting key facts")
    facts = orch.send(
        to="Researcher",
        message=f"Extract key facts from this {COMPANY} earnings material:\n\n{TRANSCRIPT}",
        from_name="User",
    )

    # Step 2 — Bull Analyst
    print("\n[Step 2/5] Bull Analyst — building the buy case")
    bull_case = orch.send(
        to="BullAnalyst",
        message=f"Build the bull case for {COMPANY} based on:\n\n{facts}",
        from_name="Researcher",
    )

    # Step 3 — Bear Analyst
    print("\n[Step 3/5] Bear Analyst — building the bear case")
    bear_case = orch.send(
        to="BearAnalyst",
        message=f"Build the bear case for {COMPANY} based on:\n\n{facts}",
        from_name="Researcher",
    )

    # Step 4 — Risk Manager stress-tests both cases
    print("\n[Step 4/5] Risk Manager — stress-testing the thesis")
    risk_assessment = orch.send(
        to="RiskManager",
        message=(
            f"Stress-test the investment thesis for {COMPANY}.\n\n"
            f"BULL CASE:\n{bull_case}\n\n"
            f"BEAR CASE:\n{bear_case}"
        ),
        from_name="Analysts",
    )

    # Step 5 — Report Writer produces the investment memo
    print("\n[Step 5/5] Report Writer — drafting investment memo")
    memo = orch.send(
        to="ReportWriter",
        message=(
            f"Write an investment memo for {COMPANY}.\n\n"
            f"FACTS:\n{facts}\n\n"
            f"BULL CASE:\n{bull_case}\n\n"
            f"BEAR CASE:\n{bear_case}\n\n"
            f"RISKS:\n{risk_assessment}"
        ),
        from_name="RiskManager",
    )

    # Save memo to file
    output_path = f"{COMPANY.lower()}_investment_memo.txt"
    with open(output_path, "w") as f:
        f.write(f"INVESTMENT MEMO — {COMPANY}\n")
        f.write("=" * 60 + "\n\n")
        f.write(memo)
    print(f"\n[Saved] Investment memo → {output_path}")

    print("\n" + "=" * 60)
    print("EARNINGS ANALYSIS COMPLETE")
    print("=" * 60)

    orch.print_log()


if __name__ == "__main__":
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Set ANTHROPIC_API_KEY in your environment or .env file.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    run_earnings_analysis(client)
