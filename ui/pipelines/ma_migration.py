"""
M&A Systems Migration Pipeline — Financial Services
====================================================
Generic template for post-acquisition technology integration.
Produces: Data mapping, gap analysis, risk assessment, migration roadmap
"""
import streamlit as st
from ui.helpers import run_agent

ACQUIRED_STACK = """Order Management System (OMS) integrated with:
- Legacy Portfolio Accounting System: portfolio accounting, performance reporting, client billing, securities master
- Legacy CRM: investor relationships, pipeline tracking, client contacts, AUM data, meeting notes
- OMS configured to feed trade data into Legacy Portfolio Accounting System"""

ACQUIRER_STACK = """Order Management System (OMS) integrated with:
- Target Portfolio Accounting System: portfolio accounting, fund accounting, investor accounting, NAV reporting
- Target Investment Management Platform: order management, portfolio management, compliance, investor CRM
- OMS configured to feed trade data into Target Portfolio Accounting and Investment Platform"""

MIGRATION_SCOPE = """
Legacy Portfolio Accounting → Target Portfolio Accounting:
All portfolio/fund accounting data, positions, transactions, securities master,
performance history, client reporting templates, billing schedules

Legacy CRM → Target Investment Platform:
All investor/client records, contact data, AUM history, interaction logs,
pipeline deals, fundraising data, investor portal access

OMS reconfiguration: Disconnect from legacy system integrations,
reconnect to target systems, validate trade flow continuity
"""


def render(client):
    st.subheader("🔄 M&A Systems Migration Planner")
    st.caption("Map data, identify gaps, assess risks, and produce a phased migration roadmap.")

    tab1, tab2, tab3 = st.tabs(["📋 Discovery & Roadmap", "🗂️ Data Field Mapping", "⚙️ OMS Reconfiguration"])

    # ── Tab 1: Discovery & Roadmap ────────────────────────────────────────────
    with tab1:
        st.markdown("#### Define the Two Application Stacks")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Acquired Company (Decommission)**")
            acquired = st.text_area("Applications being replaced",
                value=ACQUIRED_STACK, height=180)
        with col2:
            st.markdown("**Acquirer (Target State)**")
            target = st.text_area("Applications moving to",
                value=ACQUIRER_STACK, height=180)

        scope = st.text_area("Migration scope / additional context",
            value=MIGRATION_SCOPE, height=120)

        st.markdown("**Pipeline:** `Systems Analyst` → `Gap Analyzer` → `Risk Assessor` → `Roadmap Writer`")

        if st.button("▶  Generate Migration Plan", type="primary", use_container_width=True, key="btn_roadmap"):
            st.divider()

            h1: list = []
            with st.expander("🔍 Step 1 — Systems Analyst", expanded=True):
                inventory = run_agent(client, "Systems Analyst", "🔍",
                    "You are a financial technology systems analyst specialising in asset management platforms. "
                    "Given two application stacks, produce:\n"
                    "  • Functional inventory of each system (what data it holds, what processes it runs)\n"
                    "  • Data categories in each system (positions, transactions, clients, instruments, etc)\n"
                    "  • Key integrations and data flows between systems\n"
                    "  • Estimated data volumes where inferable\n"
                    "  • Regulatory and compliance dependencies (GIPS, SEC, AIFMD, etc)\n"
                    "Be specific to asset management / hedge fund operations.",
                    f"Inventory both application stacks.\n\nACQUIRED STACK:\n{acquired}\n\n"
                    f"TARGET STACK:\n{target}\n\nSCOPE:\n{scope}", h1)

            h2: list = []
            with st.expander("🔎 Step 2 — Gap Analyzer", expanded=True):
                gaps = run_agent(client, "Gap Analyzer", "🔎",
                    "You are a systems migration specialist for buy-side financial firms. "
                    "Compare the two systems and identify:\n"
                    "  • Direct equivalents (Legacy Portfolio System portfolio accounting ↔ Target Portfolio System portfolio accounting)\n"
                    "  • Functional gaps (features in old system with no direct equivalent in new)\n"
                    "  • Data model differences (how the same concept is structured differently)\n"
                    "  • Reporting gaps (reports that exist in Legacy Systems with no Target Systems equivalent)\n"
                    "  • Workflow gaps (processes that need to be rebuilt in the new system)\n"
                    "Format as a comparison table where possible. Flag CRITICAL gaps in CAPS.",
                    f"Identify gaps between the two stacks.\n\nSYSTEMS INVENTORY:\n{inventory}", h2)

            h3: list = []
            with st.expander("⚠️ Step 3 — Risk Assessor", expanded=True):
                risks = run_agent(client, "Risk Assessor", "⚠️",
                    "You are a technology risk manager for asset management firms. "
                    "Assess migration risks across:\n"
                    "  • Data integrity risks (data loss, corruption, mapping errors)\n"
                    "  • Operational continuity (trading, NAV, reporting during cutover)\n"
                    "  • Regulatory reporting continuity (GIPS performance, SEC filings, audit trail)\n"
                    "  • Client impact (investor reporting, portal access, billing)\n"
                    "  • OMS Platform reconfiguration risk (trade flow interruption)\n"
                    "  • Data history preservation (how many years of history, performance records)\n"
                    "Rate each: CRITICAL / HIGH / MEDIUM / LOW. Suggest mitigation for each CRITICAL/HIGH risk.",
                    f"Assess migration risks.\n\nSYSTEMS:\n{inventory}\n\nGAPS:\n{gaps}", h3)

            h4: list = []
            with st.expander("📋 Step 4 — Migration Roadmap", expanded=True):
                roadmap = run_agent(client, "Migration Roadmap Writer", "📋",
                    "You are a programme manager specialising in buy-side technology migrations. "
                    "Produce a phased migration roadmap:\n\n"
                    "  Phase 1 — Preparation (months 1-2)\n"
                    "  Phase 2 — Parallel Run (months 3-4): both systems live, validate outputs\n"
                    "  Phase 3 — Cutover (month 5): sequence of cutovers with go/no-go criteria\n"
                    "  Phase 4 — Decommission (month 6): shutdown and data archival\n\n"
                    "For each phase list: key activities, owners (IT/Ops/Compliance/Front Office), "
                    "dependencies, success criteria, and rollback plan.\n"
                    "Include a recommended cutover sequence: which system to migrate first and why "
                    "(recommend: Target Portfolio System beforeTarget Investment Platform, OMS reconfiguration last).",
                    f"Write phased migration roadmap.\n\nINVENTORY:\n{inventory}\n\n"
                    f"GAPS:\n{gaps}\n\nRISKS:\n{risks}", h4)

            st.success("✅ Migration roadmap complete!")
            full_output = f"MIGRATION ROADMAP\n{'='*60}\n\nSYSTEMS INVENTORY:\n{inventory}\n\n" \
                          f"GAP ANALYSIS:\n{gaps}\n\nRISK ASSESSMENT:\n{risks}\n\nROADMAP:\n{roadmap}"
            st.download_button("⬇️ Download Full Migration Plan", data=full_output,
                file_name="migration_roadmap.txt", mime="text/plain")

    # ── Tab 2: Data Field Mapping ─────────────────────────────────────────────
    with tab2:
        st.markdown("#### Data Field Mapping — Legacy Portfolio System → Target Portfolio System / Legacy CRM →Target Investment Platform")
        st.caption("Paste schema or field list from source system. Agents map to target system fields.")

        col1, col2 = st.columns(2)
        with col1:
            migration_type = st.selectbox("Migration type",
                ["Legacy Portfolio System → Target Portfolio System (Portfolio Accounting)",
                 "Legacy CRM →Target Investment Platform (Investor CRM)"])
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)

        source_schema = st.text_area("Source system fields / schema (paste table definitions, field names, or data dictionary)",
            placeholder="e.g.\nLegacy Portfolio System Portfolio table:\n  PortfolioID, PortfolioName, InceptionDate, BaseCurrency,\n  BenchmarkID, ManagerCode, FeeSchedule, Status...",
            height=200)

        if st.button("▶  Generate Field Mapping", type="primary", use_container_width=True, key="btn_mapping"):
            if not source_schema.strip():
                st.error("Please paste source system fields or schema.")
                st.stop()

            is_apx = "Legacy Portfolio System" in migration_type
            source_sys = "Legacy Portfolio Accounting System" if is_apx else "Legacy CRM"
            target_sys = "SS&C Target Portfolio System" if is_apx else "Charles RiverTarget Investment Platform"

            st.divider()
            h1: list = []
            with st.expander("🗂️ Step 1 — Schema Analyst", expanded=True):
                analysis = run_agent(client, "Schema Analyst", "🗂️",
                    f"You are a data migration specialist for {source_sys} to {target_sys} migrations "
                    "in asset management. Analyse the source schema and for each field identify:\n"
                    "  • Data type and format\n  • Business purpose\n"
                    "  • Whether it is mandatory, optional, or derived\n  • Known data quality issues",
                    f"Analyse this {source_sys} schema:\n\n{source_schema}", h1)

            h2: list = []
            with st.expander("🔀 Step 2 — Field Mapper", expanded=True):
                mapping = run_agent(client, "Field Mapper", "🔀",
                    f"You are an expert in both {source_sys} and {target_sys} data models for asset management. "
                    "For each source field produce a mapping table with columns:\n"
                    "  | Source Field | Target Field | Transformation Required | Notes |\n"
                    "Transformation types: Direct copy / Lookup / Concatenate / Split / "
                    "Calculate / Default value / No equivalent (flag as GAP)\n"
                    f"Use your knowledge of {source_sys} and {target_sys} standard data models.",
                    f"Map these {source_sys} fields to {target_sys}.\n\nSOURCE SCHEMA:\n{analysis}", h2)

            h3: list = []
            with st.expander("✅ Step 3 — Validation Plan", expanded=True):
                run_agent(client, "Validation Planner", "✅",
                    "You are a data quality engineer. Given a field mapping, produce a validation plan:\n"
                    "  • Row count reconciliation checks\n  • Key field value checks (nulls, ranges, formats)\n"
                    "  • Business rule validations (e.g. position + transaction = ending balance)\n"
                    "  • Sample reconciliation approach (% of records to manually verify)\n"
                    "  • Sign-off criteria before cutover",
                    f"Write validation plan for this mapping:\n\n{mapping}", h3)

            st.success("✅ Field mapping complete!")
            st.download_button("⬇️ Download Field Mapping", data=mapping,
                file_name=f"field_mapping_{source_sys.split()[0].lower()}_to_{target_sys.split()[0].lower()}.txt",
                mime="text/plain")

    # ── Tab 3: OMS Reconfiguration ────────────────────────────────────────────
    with tab3:
        st.markdown("#### OMS Platform Reconfiguration Plan")
        st.caption("Both firms use OMS Platform but wired to different back-office systems. "
                   "Agents produce a reconfiguration and testing plan.")

        col1, col2 = st.columns(2)
        with col1:
            current_config = st.text_area("Current OMS integrations (acquired firm)",
                value="OMS Platform OMS → Legacy Portfolio System (trade feed, positions)\nOMS Platform → Legacy CRM (client/account data)\n"
                      "FIX connections: prime brokers, executing brokers\nReporting: blotter to Legacy Portfolio System overnight batch",
                height=150)
        with col2:
            target_config = st.text_area("Target OMS integrations (acquirer)",
                value="OMS Platform OMS → Target Portfolio System (trade feed, positions)\nOMS Platform →Target Investment Platform (order management, compliance)\n"
                      "FIX connections: same prime/executing brokers\nReporting: blotter to Target Portfolio System real-time",
                height=150)

        trading_details = st.text_area("Trading environment details (optional)",
            placeholder="e.g. asset classes traded, number of portfolios, daily trade volume, prime brokers...",
            height=80)

        if st.button("▶  Generate OMS Reconfiguration Plan", type="primary", use_container_width=True, key="btn_eze"):
            st.divider()
            h1: list = []
            with st.expander("⚙️ Step 1 — Integration Analyst", expanded=True):
                eze_analysis = run_agent(client, "Integration Analyst", "⚙️",
                    "You are an OMS Platform / OMS implementation specialist. "
                    "Compare current and target integration configurations and identify:\n"
                    "  • What needs to be disconnected from Legacy Systems\n"
                    "  • What needs to be reconnected to Target Systems\n"
                    "  • FIX session changes required\n"
                    "  • Data feed mapping changes (field by field if possible)\n"
                    "  • Overnight batch process changes\n"
                    "  • User access and entitlement changes",
                    f"Analyse OMS reconfiguration requirements.\n\nCURRENT:\n{current_config}\n\n"
                    f"TARGET:\n{target_config}\n\nTRADING DETAILS:\n{trading_details or 'Not provided'}", h1)

            h2: list = []
            with st.expander("🧪 Step 2 — Testing Plan", expanded=True):
                test_plan = run_agent(client, "Testing Specialist", "🧪",
                    "You are a trading systems QA specialist. Write a cutover testing plan for "
                    "OMS Platform reconfiguration covering:\n"
                    "  • Pre-cutover testing (parallel environment)\n"
                    "  • Day 1 trading smoke tests (place order → Target Portfolio System confirms position)\n"
                    "  • End-of-day reconciliation tests (OMS blotter = Target Portfolio System positions)\n"
                    "  • FIX connectivity tests per broker\n"
                    "  • Rollback trigger criteria (what failure means we revert)\n"
                    "  • Go-live sign-off checklist",
                    f"Write testing plan for OMS reconfiguration.\n\nCHANGES:\n{eze_analysis}", h2)

            h3: list = []
            with st.expander("📋 Step 3 — Cutover Runbook", expanded=True):
                runbook = run_agent(client, "Runbook Writer", "📋",
                    "Write a step-by-step cutover runbook for the OMS Platform reconfiguration. "
                    "Format as numbered steps with:\n"
                    "  • Exact action to take\n  • Who performs it (IT / Operations / Trading Desk)\n"
                    "  • Expected outcome / verification step\n  • Time estimate\n"
                    "  • Rollback step if it fails\n"
                    "Include a pre-cutover checklist and post-cutover verification checklist. "
                    "Recommend doing this on a Friday evening after market close.",
                    f"Write cutover runbook.\n\nCHANGES:\n{eze_analysis}\n\nTESTING:\n{test_plan}", h3)

            st.success("✅ OMS reconfiguration plan complete!")
            full = f"EZE CASTLE RECONFIGURATION PLAN\n{'='*60}\n\n" \
                   f"INTEGRATION ANALYSIS:\n{eze_analysis}\n\nTESTING PLAN:\n{test_plan}\n\nRUNBOOK:\n{runbook}"
            st.download_button("⬇️ Download Runbook", data=full,
                file_name="eze_reconfiguration_runbook.txt", mime="text/plain")
