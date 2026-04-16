"""
SMB Sellability Pipeline — Business Succession & Digital Transformation
=======================================================================
Target: Retiring business owners who want to sell for maximum value
Pipeline: BusinessAudit → SellabilityScorer → SOPGenerator → BuyerReadyReport
"""
import streamlit as st
from ui.helpers import run_agent

SAMPLE_BUSINESS = """Business: Premier HVAC Services, Livingston NJ
Owner: Bob, age 64, wants to retire in 18 months
Years in business: 28 years
Annual Revenue: $1.2M
Net Profit: $180K (15% margin)
Staff: 6 field technicians, 1 office manager
Customers: ~420 active accounts (residential + small commercial)
How they run the business:
- Scheduling: paper diary + phone calls, owner manages personally
- Invoicing: QuickBooks but owner does it manually every Friday
- Customer records: mix of paper files and old ACT! database
- Job estimates: owner does all estimates from memory, no written process
- Marketing: zero — all word of mouth and repeat customers
- Key person risk: owner knows every customer personally, most won't deal with anyone else
- Contracts: no written service contracts, all handshake deals
- Equipment/assets: 4 vans (2 owned, 2 leased), $80K tools and inventory
Current asking price expectation: $500K
Broker told them: business is worth $200K as-is because it's too owner-dependent"""

def render(client):
    st.subheader("📈 Business Sellability Audit")
    st.caption(
        "For retiring business owners. Four agents assess your business, score its sellability, "
        "document your processes, and produce a report that gets you a higher sale price."
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        business_info = st.text_area(
            "Describe your business",
            value=SAMPLE_BUSINESS,
            height=280,
            help="Include: revenue, profit, staff, how you run day-to-day operations, "
                 "what systems you use, what's in your head vs written down"
        )
    with col2:
        owner_name = st.text_input("Owner name", value="Bob")
        business_name = st.text_input("Business name", value="Premier HVAC Services")
        timeline = st.selectbox("Target exit timeline",
            ["6 months", "12 months", "18 months", "2-3 years"])
        asking_price = st.text_input("Hoped-for sale price", value="$500,000")

        st.markdown("**Pipeline:**")
        st.markdown("1. 🔍 Business Auditor")
        st.markdown("2. 🏆 Sellability Scorer")
        st.markdown("3. 📋 SOP Generator")
        st.markdown("4. 📄 Buyer-Ready Report")

    if st.button("▶  Run Sellability Audit", type="primary", use_container_width=True):
        if not business_info.strip():
            st.error("Please describe the business.")
            st.stop()

        context = (
            f"Business: {business_name}\n"
            f"Owner: {owner_name}\n"
            f"Exit timeline: {timeline}\n"
            f"Asking price: {asking_price}\n\n"
            f"{business_info}"
        )

        st.divider()

        # Step 1 — Business Auditor
        h1: list = []
        with st.expander("🔍 Step 1 — Business Auditor", expanded=True):
            audit = run_agent(client, "Business Auditor", "🔍",
                "You are a business acquisition analyst who helps SMB owners prepare for sale. "
                "Given a business description, produce a structured audit covering:\n"
                "  • Revenue quality (recurring vs one-off, customer concentration risk)\n"
                "  • Profit margins vs industry benchmark\n"
                "  • Key person dependency (how much relies on the owner personally)\n"
                "  • Systems and processes (what's documented vs in owner's head)\n"
                "  • Customer relationships (contracts, loyalty, transferability)\n"
                "  • Staff and operational resilience\n"
                "  • Assets and liabilities\n"
                "  • What a buyer would see as RED FLAGS vs GREEN FLAGS\n"
                "Be specific and honest. Don't sugarcoat problems.",
                f"Audit this business for sale readiness:\n\n{context}", h1)

        # Step 2 — Sellability Scorer
        h2: list = []
        with st.expander("🏆 Step 2 — Sellability Scorer", expanded=True):
            score_report = run_agent(client, "Sellability Scorer", "🏆",
                "You are a business valuation specialist. Given a business audit, produce:\n\n"
                "  SELLABILITY SCORE: X/100\n\n"
                "  Score each dimension out of 10:\n"
                "  • Financial Performance (revenue trend, margins, cash flow)\n"
                "  • Owner Independence (can it run without them?)\n"
                "  • Documented Processes (SOPs, systems, training materials)\n"
                "  • Customer Base Quality (contracts, concentration, loyalty)\n"
                "  • Staff & Operations (team stability, skills, retention)\n"
                "  • Growth Potential (what a buyer could do with it)\n\n"
                "  For each dimension: current score, target score, and the ONE action "
                "that would have the biggest impact on improving it.\n\n"
                "  VALUATION IMPACT: Show current estimated value vs potential value "
                "after improvements. Use a 2-4x EBITDA multiple for service businesses.\n\n"
                "  PRIORITY ACTION LIST: Top 5 things to do before listing for sale, "
                "ranked by impact on sale price.",
                f"Score sellability based on this audit:\n\n{audit}", h2)

        # Step 3 — SOP Generator
        h3: list = []
        with st.expander("📋 Step 3 — SOP Generator", expanded=True):
            sops = run_agent(client, "SOP Generator", "📋",
                "You are an operations consultant who documents business processes. "
                "Given a business description, identify the 5 most critical processes "
                "that are currently in the owner's head and need to be documented. "
                "For each process write a structured SOP:\n\n"
                "  PROCESS NAME\n"
                "  Purpose: (why this matters to a buyer)\n"
                "  Trigger: (what starts this process)\n"
                "  Steps: (numbered, specific, anyone could follow)\n"
                "  Tools needed: (software, forms, equipment)\n"
                "  Output/Result: (what does done look like)\n"
                "  Common mistakes: (what goes wrong)\n\n"
                "Focus on: customer onboarding, job estimation, scheduling, "
                "invoicing/collection, and staff supervision. "
                "Write as if training a new manager who has never worked here.",
                f"Generate SOPs for the critical processes in this business:\n\n{context}\n\n"
                f"AUDIT FINDINGS:\n{audit}", h3)

        # Step 4 — Buyer-Ready Report
        h4: list = []
        with st.expander("📄 Step 4 — Buyer-Ready Report", expanded=True):
            report = run_agent(client, "Buyer-Ready Report Writer", "📄",
                "You are a business broker writing a Confidential Information Memorandum (CIM) "
                "— the document shown to serious buyers. Structure it as:\n\n"
                "  1. EXECUTIVE SUMMARY\n"
                "     One paragraph: what the business is, why it's a great acquisition, "
                "     asking price and key metrics\n\n"
                "  2. BUSINESS OVERVIEW\n"
                "     History, services, geographic market, competitive position\n\n"
                "  3. FINANCIAL HIGHLIGHTS\n"
                "     Revenue, profit, growth trend, key financial ratios\n\n"
                "  4. OPERATIONS\n"
                "     How the business runs day-to-day (reference the SOPs)\n\n"
                "  5. CUSTOMERS & MARKET\n"
                "     Customer profile, retention, growth opportunity\n\n"
                "  6. TEAM\n"
                "     Staff overview, key roles, transition plan\n\n"
                "  7. GROWTH OPPORTUNITIES\n"
                "     3 specific ways a new owner could grow revenue in year 1\n\n"
                "  8. THE ASK\n"
                "     Asking price, deal structure preference, transition support offered\n\n"
                "Write this to make the business sound genuinely attractive to a buyer "
                "while being honest. Avoid puffery. Buyers are smart.",
                f"Write a buyer-ready CIM report.\n\n"
                f"BUSINESS INFO:\n{context}\n\n"
                f"AUDIT:\n{audit}\n\n"
                f"SELLABILITY SCORE:\n{score_report}\n\n"
                f"SOPs:\n{sops}", h4)

        st.success(f"✅ Sellability audit for {business_name} complete!")

        full_report = (
            f"BUSINESS SELLABILITY AUDIT — {business_name}\n"
            f"{'='*60}\n\n"
            f"AUDIT FINDINGS:\n{audit}\n\n"
            f"SELLABILITY SCORE:\n{score_report}\n\n"
            f"STANDARD OPERATING PROCEDURES:\n{sops}\n\n"
            f"BUYER-READY REPORT (CIM):\n{report}"
        )

        st.download_button(
            "⬇️ Download Full Audit Package",
            data=full_report,
            file_name=f"{business_name.replace(' ','_').lower()}_sellability_audit.txt",
            mime="text/plain"
        )

        st.info(
            f"💡 **Your pitch to {owner_name}:** Show them the gap between their current "
            f"estimated value and what it could be after improvements. "
            f"That gap is your fee justification."
        )
