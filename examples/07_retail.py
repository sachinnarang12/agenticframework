"""
Example 7: Sales Intelligence — Retail
=======================================

Pattern: Sequential pipeline with retail domain agents
Agents:  SalesAnalyst → TrendSpotter → PricingAgent → InventoryAgent → MerchandisingWriter

Takes weekly sales data and produces an actionable merchandising report
through five specialist agents covering performance, trends, pricing, and stock.

This demonstrates:
  - Retail-specific domain prompts
  - Pricing optimisation layer
  - Inventory risk flagging
  - Buyer/merchandiser-friendly action plan

Run:
    python examples/07_retail.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import anthropic
from dotenv import load_dotenv
from agents import Agent, Orchestrator

load_dotenv()

STORE_NAME = "SportZone — 3-store chain"
SALES_DATA = """
Week: 14 Oct – 20 Oct 2024
Total Revenue: $84,300 (-4% vs prior week, -2% vs same week last year)

TOP SELLERS (units sold):
1. Nike Air Max 270 — 48 units @ $189 avg — $9,072
2. Adidas Ultraboost 22 — 31 units @ $210 avg — $6,510
3. Under Armour Hoodie (Black) — 67 units @ $89 avg — $5,963
4. Puma Running Shorts (M/L) — 89 units @ $45 avg — $4,005
5. Columbia Rain Jacket — 22 units @ $179 avg — $3,938

SLOW MOVERS (>45 days on shelf, <5 units/week):
- Reebok Classic Leather (sizes 7-8 only): 2 units, 68 days on shelf, 42 units remaining
- Speedo Goggles (tinted): 1 unit, 55 days, 28 remaining
- Columbia Hiking Boots (wide fit): 3 units, 49 days, 18 remaining

STOCK ALERTS:
- Nike Air Max 270 (sizes 9-11): 6 units remaining (3-4 days stock)
- Under Armour Hoodie Black (L/XL): 8 units remaining
- Puma Running Shorts (S size): OUT OF STOCK since Monday

MARGIN DATA:
- Average gross margin: 42%
- Lowest margin category: Footwear (38%)
- Highest margin category: Accessories (58%)

PROMOTIONS RUNNING:
- 20% off all Columbia outerwear (ends Sunday)
- Buy 2 get 1 free on Puma — driving shorts volume but margin impact

UPCOMING:
- Black Friday in 6 weeks
- New Nike Spring line arriving in 3 weeks (need clearance space)
- Store 2 (mall location) underperforming by 18% vs other stores
"""


def build_agents(client: anthropic.Anthropic) -> dict[str, Agent]:
    return {
        "SalesAnalyst": Agent(
            name="SalesAnalyst",
            system_prompt=(
                "You are a retail sales analyst. Given weekly sales data, produce:\n"
                "  • Revenue performance summary (vs prior week, vs prior year)\n"
                "  • Top 5 and bottom 5 SKUs by revenue and units\n"
                "  • Category performance breakdown\n"
                "  • Gross margin analysis\n"
                "  • Promotion effectiveness assessment\n"
                "Use tables where helpful. Flag underperformance in CAPS."
            ),
            client=client,
            model="claude-haiku-4-5-20251001",
        ),
        "TrendSpotter": Agent(
            name="TrendSpotter",
            system_prompt=(
                "You are a retail trend analyst. Given sales performance data, identify:\n"
                "  • Emerging demand signals (what's accelerating)\n"
                "  • Demand softness (what's slowing and why)\n"
                "  • Seasonal factors to prepare for\n"
                "  • Customer behaviour patterns\n"
                "  • Competitive context (if inferable)\n"
                "Distinguish between short-term spikes and genuine trend shifts."
            ),
            client=client,
            model="claude-haiku-4-5-20251001",
        ),
        "PricingAgent": Agent(
            name="PricingAgent",
            system_prompt=(
                "You are a retail pricing strategist. Given sales and margin data, recommend:\n"
                "  • Markdowns for slow movers (with % and rationale)\n"
                "  • Price holds or increases for fast movers with pricing power\n"
                "  • Promotion assessment (which promos to extend, cut, or adjust)\n"
                "  • Margin improvement opportunities\n"
                "Be specific: name the SKU, recommend the action, give the expected outcome."
            ),
            client=client,
            model="claude-haiku-4-5-20251001",
        ),
        "InventoryAgent": Agent(
            name="InventoryAgent",
            system_prompt=(
                "You are an inventory and replenishment specialist. Given stock data, identify:\n"
                "  • Urgent reorder needs (days of stock remaining)\n"
                "  • Overstock / dead stock requiring clearance\n"
                "  • Size curve issues (wrong sizes in stock)\n"
                "  • Space optimisation recommendations\n"
                "  • Replenishment quantities for top sellers\n"
                "Prioritise by urgency: URGENT / THIS WEEK / THIS MONTH."
            ),
            client=client,
            model="claude-haiku-4-5-20251001",
        ),
        "MerchandisingWriter": Agent(
            name="MerchandisingWriter",
            system_prompt=(
                "You are a head of merchandising writing a weekly trade report. "
                "Structure your report as:\n"
                "  1. Week in Review (2-3 sentences)\n"
                "  2. Priority Actions This Week (numbered, owner assigned)\n"
                "  3. Pricing & Promotions Decisions\n"
                "  4. Replenishment Orders Needed\n"
                "  5. Black Friday Preparation Checklist\n"
                "  6. Store 2 Recovery Plan\n"
                "Be direct and specific. Buyers should be able to act on this immediately."
            ),
            client=client,
            model="claude-haiku-4-5-20251001",
        ),
    }


def run_retail_analysis(client: anthropic.Anthropic) -> None:
    agents = build_agents(client)

    orch = Orchestrator(verbose=True)
    for agent in agents.values():
        orch.register(agent)

    print("\n" + "=" * 60)
    print(f"RETAIL SALES INTELLIGENCE: {STORE_NAME}")
    print("=" * 60)

    print("\n[Step 1/5] Sales Analyst — performance breakdown")
    sales_summary = orch.send(
        to="SalesAnalyst",
        message=f"Analyse weekly sales data for {STORE_NAME}:\n\n{SALES_DATA}",
        from_name="User",
    )

    print("\n[Step 2/5] Trend Spotter — demand signals")
    trend_insights = orch.send(
        to="TrendSpotter",
        message=(
            f"Identify trends and demand signals for {STORE_NAME}.\n\n"
            f"SALES ANALYSIS:\n{sales_summary}"
        ),
        from_name="SalesAnalyst",
    )

    print("\n[Step 3/5] Pricing Agent — markdown and pricing decisions")
    pricing_plan = orch.send(
        to="PricingAgent",
        message=(
            f"Recommend pricing actions for {STORE_NAME}.\n\n"
            f"SALES SUMMARY:\n{sales_summary}\n\n"
            f"TRENDS:\n{trend_insights}"
        ),
        from_name="TrendSpotter",
    )

    print("\n[Step 4/5] Inventory Agent — stock alerts and replenishment")
    inventory_plan = orch.send(
        to="InventoryAgent",
        message=(
            f"Assess inventory position for {STORE_NAME}.\n\n"
            f"SALES DATA:\n{SALES_DATA}\n\n"
            f"PRICING ACTIONS:\n{pricing_plan}"
        ),
        from_name="PricingAgent",
    )

    print("\n[Step 5/5] Merchandising Writer — weekly trade report")
    trade_report = orch.send(
        to="MerchandisingWriter",
        message=(
            f"Write the weekly trade report for {STORE_NAME}.\n\n"
            f"SALES ANALYSIS:\n{sales_summary}\n\n"
            f"TRENDS:\n{trend_insights}\n\n"
            f"PRICING:\n{pricing_plan}\n\n"
            f"INVENTORY:\n{inventory_plan}"
        ),
        from_name="InventoryAgent",
    )

    output_path = "retail_trade_report.txt"
    with open(output_path, "w") as f:
        f.write(f"WEEKLY TRADE REPORT — {STORE_NAME}\n")
        f.write("=" * 60 + "\n\n")
        f.write(trade_report)
    print(f"\n[Saved] Trade report → {output_path}")

    print("\n" + "=" * 60)
    print("RETAIL ANALYSIS COMPLETE")
    print("=" * 60)
    orch.print_log()


if __name__ == "__main__":
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Set ANTHROPIC_API_KEY in your environment or .env file.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    run_retail_analysis(client)
