"""
Example 6: Financial Health Review — Small Business
====================================================

Pattern: Sequential pipeline with small business finance agents
Agents:  BookkeeperAgent → CashFlowAgent → AdvisorAgent → ActionPlanWriter

Takes a business's monthly financial data and produces an actionable
owner-friendly financial review through four specialist agents.

This demonstrates:
  - Plain-English output for non-finance audiences
  - Cash flow forecasting layer
  - Actionable recommendations (not just analysis)

Run:
    python examples/06_small_business.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import anthropic
from dotenv import load_dotenv
from agents import Agent, Orchestrator

load_dotenv()

BUSINESS_NAME = "Joe's Plumbing & Heating"
FINANCIAL_DATA = """
Monthly Revenue: $48,200
Monthly Expenses:
  - Staff wages: $18,500 (3 employees + owner draw $4,000)
  - Materials/parts: $9,400
  - Vehicle running costs: $1,800
  - Insurance: $950
  - Tools & equipment: $600
  - Marketing (Google Ads): $800
  - Accounting software: $120
  - Phone/internet: $180
  - Miscellaneous: $430
Total Expenses: $32,780
Net Profit: $15,420

Bank Balance: $22,000
Outstanding invoices (receivables): $14,600 (avg 35 days overdue)
Credit card debt: $8,200 (18% APR)
Equipment loan: $24,000 remaining (36 months @ $720/month)

Upcoming costs next 90 days:
  - Van service & tyres: ~$2,200
  - Quarterly tax payment: ~$6,500
  - Staff bonus (Christmas): ~$3,000

Top 3 customers by revenue: 1 commercial contract ($12k/month), 2 repeat residential
Biggest headaches: late-paying customers, finding skilled staff, parts supply delays
"""


def build_agents(client: anthropic.Anthropic) -> dict[str, Agent]:
    return {
        "BookkeeperAgent": Agent(
            name="BookkeeperAgent",
            system_prompt=(
                "You are an experienced bookkeeper. Given business financial data, organise:\n"
                "  • Revenue vs expenses breakdown with percentages\n"
                "  • Gross margin and net margin\n"
                "  • Key financial ratios (current ratio, debt load)\n"
                "  • Any anomalies or areas of concern\n"
                "  • Comparison benchmarks for this type of trade business\n"
                "Use clear tables and bullet points. Flag issues in CAPS."
            ),
            client=client,
            model="claude-haiku-4-5-20251001",
        ),
        "CashFlowAgent": Agent(
            name="CashFlowAgent",
            system_prompt=(
                "You are a cash flow specialist. Given financial data, produce:\n"
                "  • 30 / 60 / 90 day cash position forecast\n"
                "  • Key cash flow risks (late payments, seasonal dips, upcoming costs)\n"
                "  • Cash runway (how many months of expenses are covered)\n"
                "  • Receivables analysis and collection risk\n"
                "Be specific with numbers. Flag any months where cash may go negative."
            ),
            client=client,
            model="claude-haiku-4-5-20251001",
        ),
        "AdvisorAgent": Agent(
            name="AdvisorAgent",
            system_prompt=(
                "You are a small business financial advisor. Given financial analysis "
                "and cash flow forecast, identify:\n"
                "  • Top 3 cost reduction opportunities with estimated savings\n"
                "  • Top 3 revenue growth actions\n"
                "  • Debt management priorities\n"
                "  • Quick wins (actions the owner can take this week)\n"
                "Be practical and specific. No generic advice — tailor to this business."
            ),
            client=client,
            model="claude-haiku-4-5-20251001",
        ),
        "ActionPlanWriter": Agent(
            name="ActionPlanWriter",
            system_prompt=(
                "You are a business coach who writes clear, motivating action plans. "
                "Structure the plan as:\n"
                "  1. Your Business Snapshot (one paragraph, plain English)\n"
                "  2. The Good News\n"
                "  3. What Needs Attention\n"
                "  4. Your 30-Day Action List (numbered, specific tasks)\n"
                "  5. Your 90-Day Goals\n"
                "  6. One Thing To Do Today\n"
                "Write as if speaking directly to the business owner. "
                "Be encouraging but honest. No jargon."
            ),
            client=client,
            model="claude-haiku-4-5-20251001",
        ),
    }


def run_small_business_review(client: anthropic.Anthropic) -> None:
    agents = build_agents(client)

    orch = Orchestrator(verbose=True)
    for agent in agents.values():
        orch.register(agent)

    print("\n" + "=" * 60)
    print(f"SMALL BUSINESS REVIEW: {BUSINESS_NAME}")
    print("=" * 60)

    print("\n[Step 1/4] Bookkeeper — organising financials")
    financial_summary = orch.send(
        to="BookkeeperAgent",
        message=f"Organise and analyse the financials for {BUSINESS_NAME}:\n\n{FINANCIAL_DATA}",
        from_name="User",
    )

    print("\n[Step 2/4] Cash Flow Agent — forecasting cash position")
    cash_forecast = orch.send(
        to="CashFlowAgent",
        message=(
            f"Forecast cash flow for {BUSINESS_NAME}.\n\n"
            f"FINANCIAL SUMMARY:\n{financial_summary}\n\n"
            f"RAW DATA:\n{FINANCIAL_DATA}"
        ),
        from_name="BookkeeperAgent",
    )

    print("\n[Step 3/4] Advisor — identifying actions")
    recommendations = orch.send(
        to="AdvisorAgent",
        message=(
            f"Provide strategic advice for {BUSINESS_NAME}.\n\n"
            f"FINANCIAL SUMMARY:\n{financial_summary}\n\n"
            f"CASH FLOW FORECAST:\n{cash_forecast}"
        ),
        from_name="CashFlowAgent",
    )

    print("\n[Step 4/4] Action Plan Writer — owner-friendly summary")
    action_plan = orch.send(
        to="ActionPlanWriter",
        message=(
            f"Write an action plan for the owner of {BUSINESS_NAME}.\n\n"
            f"FINANCIAL SUMMARY:\n{financial_summary}\n\n"
            f"CASH FLOW:\n{cash_forecast}\n\n"
            f"RECOMMENDATIONS:\n{recommendations}"
        ),
        from_name="AdvisorAgent",
    )

    output_path = f"{BUSINESS_NAME.lower().replace(' ', '_')}_action_plan.txt"
    with open(output_path, "w") as f:
        f.write(f"FINANCIAL REVIEW — {BUSINESS_NAME}\n")
        f.write("=" * 60 + "\n\n")
        f.write(action_plan)
    print(f"\n[Saved] Action plan → {output_path}")

    print("\n" + "=" * 60)
    print("SMALL BUSINESS REVIEW COMPLETE")
    print("=" * 60)
    orch.print_log()


if __name__ == "__main__":
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Set ANTHROPIC_API_KEY in your environment or .env file.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    run_small_business_review(client)
