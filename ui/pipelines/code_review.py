"""Code Review Pipeline."""
import streamlit as st
from ui.helpers import run_agent


def render(client):
    st.subheader("🔧 Code Review Pipeline")
    st.caption("Architect designs → Coder implements → Reviewer critiques → Coder revises.")

    task = st.text_area("What should be built?",
        value="a rate-limited in-memory cache with TTL expiry and thread-safety in Python",
        height=80)
    st.markdown("**Pipeline:** `Architect` → `Coder` → `Reviewer` → `Coder (revised)`")

    if st.button("▶  Run Pipeline", type="primary", use_container_width=True):
        arch_prompt = ("You are a senior software architect. Produce a concise technical design: "
                       "data structures, class/function signatures, edge cases. No full code.")
        code_prompt = ("You are an expert Python developer. Write clean, production-quality Python "
                       "with docstrings and type hints. Output ONLY the code block.")
        rev_prompt = ("You are a meticulous code reviewer. Identify bugs, edge cases, style violations, "
                      "security and performance issues. Numbered list with line references.")

        a_hist: list = []
        c_hist: list = []
        r_hist: list = []
        st.divider()

        with st.expander("🏗️ Step 1 — Architect", expanded=True):
            design = run_agent(client, "Architect", "🏗️", arch_prompt,
                f"Design a solution for: {task}", a_hist)

        with st.expander("💻 Step 2 — Coder", expanded=True):
            code = run_agent(client, "Coder", "💻", code_prompt,
                f"Implement this design as Python:\n\n{design}", c_hist)

        with st.expander("🔍 Step 3 — Reviewer", expanded=True):
            review = run_agent(client, "Reviewer", "🔍", rev_prompt,
                f"Review this code:\n\n{code}", r_hist)

        with st.expander("✅ Step 4 — Revised Code", expanded=True):
            run_agent(client, "Coder (revised)", "✅", code_prompt,
                f"Fix all issues from this review:\nREVIEW:\n{review}\nCODE:\n{code}", c_hist)

        st.success("Pipeline complete! Final code is in Step 4.")
