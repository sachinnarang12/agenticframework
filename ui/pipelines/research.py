"""Research Team pipeline."""
import streamlit as st
from ui.helpers import run_agent


def render(client):
    st.subheader("📊 Research Team")
    st.caption("3 specialist researchers → Analyst → Writer.")

    topic = st.text_input("Research topic",
        value="the impact of large language models on software engineering workflows")
    st.markdown("**Pipeline:** `TechResearcher` + `ImpactResearcher` + `FutureResearcher` → `Analyst` → `Writer`")

    if st.button("▶  Run Research", type="primary", use_container_width=True):
        researchers = {
            "TechResearcher":   ("🔬", "You are a technical research specialist. Surface important technical facts, tools, and patterns. Bullet points."),
            "ImpactResearcher": ("🌍", "You are an industry impact researcher. Identify who is affected, workflow changes, case studies. Bullet points."),
            "FutureResearcher": ("🔮", "You are a foresight researcher. Identify emerging trends, open questions, risks on a 2-5 year horizon. Bullet points."),
        }

        st.divider()
        st.markdown("#### Phase 1 — Parallel Research")
        findings: dict = {}
        for name, (icon, prompt) in researchers.items():
            hist: list = []
            with st.expander(f"{icon} {name}", expanded=True):
                findings[name] = run_agent(client, name, icon, prompt,
                    f"Research from your specialist perspective:\nTOPIC: {topic}", hist)

        combined = "\n\n".join(f"=== {n} ===\n{f}" for n, f in findings.items())

        st.markdown("#### Phase 2 — Analysis")
        a_hist: list = []
        with st.expander("📈 Analyst — Key Insights", expanded=True):
            insights = run_agent(client, "Analyst", "📈",
                "You are a senior analyst. Distil 5-7 cross-cutting insights. "
                "Format: numbered list with bold headline + explanation.",
                f"Research notes on '{topic}':\n\n{combined}", a_hist)

        st.markdown("#### Phase 3 — Report")
        w_hist: list = []
        with st.expander("✍️ Writer — Final Report", expanded=True):
            run_agent(client, "Writer", "✍️",
                "You are a technology journalist. Write a clear structured report: "
                "introduction, titled sections, forward-looking conclusion.",
                f"Write report on '{topic}' based on:\n\n{insights}", w_hist)

        st.success("Research complete!")
