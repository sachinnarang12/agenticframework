"""Small Business: Financial Health Review pipeline."""
import streamlit as st
from ui.helpers import run_agent

SAMPLE_DATA = """Monthly Revenue: $48,200
Expenses: Wages $18,500 | Materials $9,400 | Vehicles $1,800 | Insurance $950
Marketing $800 | Software $120 | Other $1,210 | Total $32,780
Net Profit: $15,420 | Bank Balance: $22,000
Receivables: $14,600 (avg 35 days overdue)
Debt: Credit card $8,200 @ 18% APR | Equipment loan $24,000 (36 months)
Upcoming 90 days: Van service $2,200 | Tax payment $6,500 | Staff bonus $3,000"""


def render(client):
    st.subheader("💼 Financial Health Review — Small Business")
    st.caption("Paste your monthly financials. Four agents produce an owner-friendly action plan.")

    col1, col2 = st.columns([2, 1])
    with col1:
        data = st.text_area("Business financial data", value=SAMPLE_DATA, height=200)
    with col2:
        biz_name = st.text_input("Business name", value="My Business")
        st.markdown("**Pipeline:**\n1. 📒 Bookkeeper\n2. 💵 Cash Flow\n"
                    "3. 🎯 Advisor\n4. 📝 Action Plan")

    if st.button("▶  Analyse", type="primary", use_container_width=True):
        if not data.strip():
            st.error("Please enter financial data.")
            st.stop()
        st.divider()

        h1: list = []
        with st.expander("📒 Step 1 — Bookkeeper", expanded=True):
            summary = run_agent(client, "Bookkeeper", "📒",
                "You are an experienced bookkeeper. Organise revenue vs expenses with percentages, "
                "gross/net margins, key ratios. Flag issues in CAPS.",
                f"Organise financials for {biz_name}:\n\n{data}", h1)

        h2: list = []
        with st.expander("💵 Step 2 — Cash Flow Forecast", expanded=True):
            cashflow = run_agent(client, "Cash Flow Agent", "💵",
                "You are a cash flow specialist. Produce 30/60/90 day forecast, flag any months "
                "where cash may go negative, assess receivables risk.",
                f"Forecast cash flow for {biz_name}.\nFINANCIALS:\n{summary}\nRAW DATA:\n{data}", h2)

        h3: list = []
        with st.expander("🎯 Step 3 — Business Advisor", expanded=True):
            advice = run_agent(client, "Advisor", "🎯",
                "You are a small business advisor. Give top 3 cost cuts with savings estimates, "
                "top 3 revenue actions, debt priorities, and quick wins for this week.",
                f"Advise {biz_name}.\nFINANCIALS:\n{summary}\nCASH FLOW:\n{cashflow}", h3)

        h4: list = []
        with st.expander("📝 Step 4 — Action Plan", expanded=True):
            plan = run_agent(client, "Action Plan Writer", "📝",
                "Write an owner-friendly action plan: 1.Business Snapshot 2.Good News "
                "3.What Needs Attention 4.30-Day Action List 5.90-Day Goals 6.One Thing To Do Today. "
                "Plain English, no jargon, speak directly to the owner.",
                f"Write action plan for {biz_name}.\nSUMMARY:\n{summary}\n"
                f"CASH FLOW:\n{cashflow}\nADVICE:\n{advice}", h4)

        st.success("✅ Business review complete!")
        st.download_button("⬇️ Download Action Plan", data=plan,
            file_name=f"{biz_name.replace(' ','_')}_action_plan.txt", mime="text/plain")
