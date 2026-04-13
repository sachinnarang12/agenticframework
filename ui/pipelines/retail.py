"""Retail: Sales Intelligence pipeline."""
import streamlit as st
from ui.helpers import run_agent

SAMPLE_DATA = """Week: 14-20 Oct 2024 | Total Revenue: $84,300 (-4% WoW)
Top sellers: Nike Air Max 270 (48 units $189), UA Hoodie Black (67 units $89)
Slow movers: Reebok Classic (2 units, 68 days shelf), Speedo Goggles (1 unit, 55 days)
Stock alerts: Nike Air Max size 9-11 (6 units left), Puma Shorts S (OUT OF STOCK)
Avg gross margin: 42% | Footwear 38% | Accessories 58%
Promotions: 20% off Columbia outerwear | Buy 2 get 1 Puma
Upcoming: Black Friday in 6 weeks | New Nike Spring line in 3 weeks"""


def render(client):
    st.subheader("🛍️ Sales Intelligence — Retail")
    st.caption("Paste weekly sales data. Five agents produce a merchandising action report.")

    col1, col2 = st.columns([2, 1])
    with col1:
        data = st.text_area("Weekly sales data", value=SAMPLE_DATA, height=200)
    with col2:
        store = st.text_input("Store / chain name", value="My Store")
        st.markdown("**Pipeline:**\n1. 📊 Sales Analyst\n2. 📈 Trend Spotter\n"
                    "3. 🏷️ Pricing Agent\n4. 📦 Inventory Agent\n5. 📋 Trade Report")

    if st.button("▶  Analyse", type="primary", use_container_width=True):
        if not data.strip():
            st.error("Please enter sales data.")
            st.stop()
        st.divider()

        h1: list = []
        with st.expander("📊 Step 1 — Sales Analyst", expanded=True):
            sales = run_agent(client, "Sales Analyst", "📊",
                "You are a retail sales analyst. Summarise revenue performance, top/bottom SKUs, "
                "category breakdown, margin analysis, promotion effectiveness. Flag issues in CAPS.",
                f"Analyse weekly sales for {store}:\n\n{data}", h1)

        h2: list = []
        with st.expander("📈 Step 2 — Trend Spotter", expanded=True):
            trends = run_agent(client, "Trend Spotter", "📈",
                "You are a retail trend analyst. Identify accelerating demand, softness, "
                "seasonal factors, and customer behaviour patterns.",
                f"Identify trends for {store}.\nSALES:\n{sales}", h2)

        h3: list = []
        with st.expander("🏷️ Step 3 — Pricing Agent", expanded=True):
            pricing = run_agent(client, "Pricing Agent", "🏷️",
                "You are a retail pricing strategist. Recommend specific markdowns for slow movers, "
                "price holds for fast movers, which promos to extend or cut. Name the SKU, give % and rationale.",
                f"Pricing recommendations for {store}.\nSALES:\n{sales}\nTRENDS:\n{trends}", h3)

        h4: list = []
        with st.expander("📦 Step 4 — Inventory Agent", expanded=True):
            inventory = run_agent(client, "Inventory Agent", "📦",
                "You are an inventory specialist. Flag urgent reorders, overstock, size curve issues. "
                "Prioritise: URGENT / THIS WEEK / THIS MONTH.",
                f"Assess inventory for {store}.\nDATA:\n{data}\nPRICING:\n{pricing}", h4)

        h5: list = []
        with st.expander("📋 Step 5 — Weekly Trade Report", expanded=True):
            report = run_agent(client, "Merchandising Writer", "📋",
                "Write a weekly trade report: 1.Week in Review 2.Priority Actions This Week "
                "3.Pricing Decisions 4.Replenishment Orders 5.Black Friday Prep. Direct and actionable.",
                f"Write trade report for {store}.\nSALES:\n{sales}\nTRENDS:\n{trends}\n"
                f"PRICING:\n{pricing}\nINVENTORY:\n{inventory}", h5)

        st.success("✅ Retail report complete!")
        st.download_button("⬇️ Download Report", data=report,
            file_name=f"{store.replace(' ','_')}_trade_report.txt", mime="text/plain")
