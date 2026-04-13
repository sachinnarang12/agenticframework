"""Agent Debate pipeline."""
import streamlit as st
from ui.helpers import run_agent


def render(client):
    st.subheader("💬 Two-Agent Debate")
    st.caption("Two agents argue opposing sides. A moderator synthesises the conclusion.")

    col1, col2 = st.columns([3, 1])
    with col1:
        topic = st.text_input("Debate topic",
            value="AI will fundamentally improve human creativity rather than replace it")
    with col2:
        rounds = st.selectbox("Rounds", [1, 2, 3], index=1)

    st.markdown("**Pipeline:** `Optimist` ↔ `Skeptic` *(N rounds)* → `Moderator`")

    if st.button("▶  Start Debate", type="primary", use_container_width=True):
        opt_prompt = ("You are an enthusiastic advocate who believes AI augments human creativity. "
                      "Support with concrete examples. 2-3 paragraphs.")
        skep_prompt = ("You are a thoughtful critic who challenges optimistic AI claims. "
                       "Raise concerns about disruption and loss of agency. 2-3 paragraphs.")
        mod_prompt = ("You are an impartial moderator. Identify strongest points from each side "
                      "and offer a nuanced synthesis. 3-4 paragraphs.")

        opt_hist: list = []
        skep_hist: list = []
        st.divider()

        with st.expander("🟢 Opening — Optimist", expanded=True):
            opt = run_agent(client, "Optimist", "🟢", opt_prompt,
                f"Give your opening argument FOR: '{topic}'", opt_hist)

        with st.expander("🔴 Opening — Skeptic", expanded=True):
            skep = run_agent(client, "Skeptic", "🔴", skep_prompt,
                f"The Optimist argued:\n{opt}\n\nGive your counter-argument.", skep_hist)

        for r in range(1, rounds + 1):
            with st.expander(f"🟢 Round {r} — Optimist", expanded=True):
                opt = run_agent(client, "Optimist", "🟢", opt_prompt,
                    f"The Skeptic said:\n{skep}\n\nRebut their points.", opt_hist)
            with st.expander(f"🔴 Round {r} — Skeptic", expanded=True):
                skep = run_agent(client, "Skeptic", "🔴", skep_prompt,
                    f"The Optimist said:\n{opt}\n\nChallenge their arguments.", skep_hist)

        mod_hist: list = []
        with st.expander("⚖️ Moderator Synthesis", expanded=True):
            run_agent(client, "Moderator", "⚖️", mod_prompt,
                f"Topic: '{topic}'\nOptimist final:\n{opt}\nSkeptic final:\n{skep}\n"
                "Synthesise both sides.", mod_hist)

        st.success("Debate complete!")
