"""Finance: Earnings Analysis pipeline."""
import streamlit as st
from ui.helpers import run_agent


def render(client):
    st.subheader("💰 Earnings Analysis — Finance")
    st.caption("Paste an earnings transcript. Five agents produce a full investment memo.")

    col1, col2 = st.columns([2, 1])
    with col1:
        transcript = st.text_area("Earnings transcript / company description",
            placeholder="Paste earnings call transcript here...", height=200)
    with col2:
        company = st.text_input("Company name", value="Apple")
        st.markdown("**Pipeline:**\n1. 🔍 Researcher\n2. 🐂 Bull Analyst\n3. 🐻 Bear Analyst\n4. ⚠️ Risk Manager\n5. 📋 Report Writer")

    if st.button("▶  Analyse", type="primary", use_container_width=True):
        if not transcript.strip():
            st.error("Please paste a transcript.")
            st.stop()
        st.divider()

        r_hist: list = []
        with st.expander("🔍 Step 1 — Researcher", expanded=True):
            facts = run_agent(client, "Researcher", "🔍",
                "You are a financial research analyst. Extract revenue, earnings, margins, "
                "guidance, segment performance, surprises. Use bullet points with numbers.",
                f"Extract key facts from this {company} earnings material:\n\n{transcript}", r_hist)

        b_hist: list = []
        with st.expander("🐂 Step 2 — Bull Analyst", expanded=True):
            bull = run_agent(client, "Bull Analyst", "🐂",
                "You are a bullish equity analyst. Build the strongest buy case: growth "
                "catalysts, moat, valuation support. Bullet points with evidence.",
                f"Build the bull case for {company}:\n\n{facts}", b_hist)

        be_hist: list = []
        with st.expander("🐻 Step 3 — Bear Analyst", expanded=True):
            bear = run_agent(client, "Bear Analyst", "🐻",
                "You are a bearish equity analyst. Build the strongest case against: risks, "
                "deceleration, competition, red flags. Bullet points with evidence.",
                f"Build the bear case for {company}:\n\n{facts}", be_hist)

        risk_hist: list = []
        with st.expander("⚠️ Step 4 — Risk Manager", expanded=True):
            risks = run_agent(client, "Risk Manager", "⚠️",
                "You are a portfolio risk manager. Identify top 5 risks, assign "
                "likelihood and impact (Low/Medium/High), suggest hedges.",
                f"Stress-test thesis for {company}.\nBULL:\n{bull}\nBEAR:\n{bear}", risk_hist)

        rep_hist: list = []
        with st.expander("📋 Step 5 — Investment Memo", expanded=True):
            memo = run_agent(client, "Report Writer", "📋",
                "You are a senior portfolio manager. Write memo: 1.Executive Summary "
                "(Buy/Hold/Sell) 2.Key Facts 3.Bull Case 4.Bear Case 5.Risks 6.Recommendation.",
                f"Write investment memo for {company}.\nFACTS:\n{facts}\nBULL:\n{bull}\n"
                f"BEAR:\n{bear}\nRISKS:\n{risks}", rep_hist)

        st.success(f"✅ Investment memo for {company} complete!")
        st.download_button("⬇️ Download Memo", data=memo,
            file_name=f"{company}_investment_memo.txt", mime="text/plain")
