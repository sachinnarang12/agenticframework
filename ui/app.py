"""
Multi-Agent AI Framework — Streamlit UI
=========================================

A user-friendly web interface for running multi-agent pipelines.

Run:
    streamlit run ui/app.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import anthropic
import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Multi-Agent AI Framework",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .agent-card {
        background: #1e1e2e;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border-left: 4px solid #7c3aed;
    }
    .agent-label {
        font-size: 13px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #a78bfa;
        margin-bottom: 6px;
    }
    .pipeline-arrow {
        text-align: center;
        font-size: 22px;
        color: #6b7280;
        margin: 4px 0;
    }
    .status-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 99px;
        font-size: 12px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ── Helper: stream one agent response into a Streamlit container ──────────────

def stream_agent(
    client: anthropic.Anthropic,
    system_prompt: str,
    messages: list,
    model: str = "claude-opus-4-6",
    max_tokens: int = 8192,
):
    """Generator that yields text chunks from the Claude streaming API."""
    with client.messages.stream(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            yield text


def run_agent(
    client: anthropic.Anthropic,
    name: str,
    icon: str,
    system_prompt: str,
    user_message: str,
    history: list,
    model: str = "claude-opus-4-6",
) -> str:
    """
    Display an agent card, stream the response into it, and return the full text.
    Updates `history` in place for multi-turn context.
    """
    st.markdown(f'<div class="agent-label">{icon} {name}</div>', unsafe_allow_html=True)

    history.append({"role": "user", "content": user_message})

    with st.container():
        full_response = st.write_stream(
            stream_agent(client, system_prompt, history, model)
        )

    history.append({"role": "assistant", "content": full_response})
    return full_response


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.image("https://www.anthropic.com/favicon.ico", width=32)
    st.title("Multi-Agent AI")
    st.caption("Powered by Claude")

    st.divider()

    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-...",
        help="Get your key at console.anthropic.com",
    )

    st.divider()

    example = st.radio(
        "Choose a pipeline",
        options=[
            "💬  Agent Debate",
            "🔧  Code Review Pipeline",
            "📊  Research Team",
            "💰  Earnings Analysis  ← Finance",
        ],
        index=3,
    )

    st.divider()
    st.caption("Each agent is a separate Claude instance with its own role and memory.")


# ── Main area ─────────────────────────────────────────────────────────────────

st.title("🤖 Multi-Agent AI Framework")

# ── Example: Agent Debate ─────────────────────────────────────────────────────
if "Debate" in example:
    st.subheader("💬 Two-Agent Debate")
    st.caption("Two agents argue opposing sides. A moderator synthesises the conclusion.")

    col1, col2 = st.columns([3, 1])
    with col1:
        topic = st.text_input(
            "Debate topic",
            value="AI will fundamentally improve human creativity rather than replace it",
        )
    with col2:
        rounds = st.selectbox("Rounds", [1, 2, 3], index=1)

    # Pipeline diagram
    st.markdown("""
    **Pipeline:**  `Optimist` ↔ `Skeptic`  *(N rounds)*  →  `Moderator`
    """)

    if st.button("▶  Start Debate", type="primary", use_container_width=True):
        if not api_key:
            st.error("Enter your API key in the sidebar.")
            st.stop()

        client = anthropic.Anthropic(api_key=api_key)

        optimist_prompt = (
            "You are an enthusiastic advocate who believes AI will augment human "
            "creativity. Support your arguments with concrete examples. "
            "Keep responses to 2-3 focused paragraphs."
        )
        skeptic_prompt = (
            "You are a thoughtful critic who challenges optimistic AI claims. "
            "Raise concerns about economic disruption and loss of human agency. "
            "Keep responses to 2-3 focused paragraphs."
        )
        moderator_prompt = (
            "You are an impartial debate moderator. Given the full debate, identify "
            "the strongest points from each side and offer a nuanced synthesis. "
            "Write 3-4 paragraphs."
        )

        optimist_hist: list = []
        skeptic_hist:  list = []

        st.divider()

        # Opening
        with st.expander("🟢 Opening Statement — Optimist", expanded=True):
            opt_response = run_agent(
                client, "Optimist", "🟢", optimist_prompt,
                f"Give your opening argument FOR: '{topic}'",
                optimist_hist,
            )

        with st.expander("🔴 Opening Statement — Skeptic", expanded=True):
            skep_response = run_agent(
                client, "Skeptic", "🔴", skeptic_prompt,
                f"The Optimist argued:\n\n{opt_response}\n\nGive your counter-argument.",
                skeptic_hist,
            )

        # Rounds
        for r in range(1, rounds + 1):
            with st.expander(f"🟢 Round {r} — Optimist", expanded=True):
                opt_response = run_agent(
                    client, "Optimist", "🟢", optimist_prompt,
                    f"The Skeptic said:\n\n{skep_response}\n\nRebut their points.",
                    optimist_hist,
                )
            with st.expander(f"🔴 Round {r} — Skeptic", expanded=True):
                skep_response = run_agent(
                    client, "Skeptic", "🔴", skeptic_prompt,
                    f"The Optimist said:\n\n{opt_response}\n\nChallenge their arguments.",
                    skeptic_hist,
                )

        # Moderator
        mod_hist: list = []
        with st.expander("⚖️ Moderator Synthesis", expanded=True):
            run_agent(
                client, "Moderator", "⚖️", moderator_prompt,
                (
                    f"Debate topic: '{topic}'\n\n"
                    f"Optimist's final position:\n{opt_response}\n\n"
                    f"Skeptic's final position:\n{skep_response}\n\n"
                    "Please synthesise both sides into a balanced conclusion."
                ),
                mod_hist,
            )

        st.success("Debate complete!")


# ── Example: Code Review Pipeline ─────────────────────────────────────────────
elif "Code" in example:
    st.subheader("🔧 Code Review Pipeline")
    st.caption("Architect designs → Coder implements → Reviewer critiques → Coder revises.")

    task = st.text_area(
        "What should be built?",
        value="a rate-limited in-memory cache with TTL expiry and thread-safety in Python",
        height=80,
    )

    st.markdown("**Pipeline:**  `Architect` → `Coder` → `Reviewer` → `Coder (revised)`")

    if st.button("▶  Run Pipeline", type="primary", use_container_width=True):
        if not api_key:
            st.error("Enter your API key in the sidebar.")
            st.stop()

        client = anthropic.Anthropic(api_key=api_key)

        architect_prompt = (
            "You are a senior software architect. Given a feature request, produce a "
            "concise technical design: data structures, class/function signatures, "
            "edge cases to handle. Do NOT write full code — only the blueprint."
        )
        coder_prompt = (
            "You are an expert Python developer. Given a design plan, write clean, "
            "idiomatic, production-quality Python code with docstrings and type hints. "
            "Output ONLY the code block."
        )
        reviewer_prompt = (
            "You are a meticulous code reviewer. Identify bugs, missing edge cases, "
            "style violations, security concerns, and performance issues. "
            "Format as a numbered list with specific line references."
        )

        architect_hist: list = []
        coder_hist:     list = []
        reviewer_hist:  list = []

        st.divider()

        with st.expander("🏗️  Step 1 — Architect designs", expanded=True):
            design = run_agent(
                client, "Architect", "🏗️", architect_prompt,
                f"Design a solution for: {task}",
                architect_hist,
            )

        st.markdown('<div class="pipeline-arrow">↓</div>', unsafe_allow_html=True)

        with st.expander("💻  Step 2 — Coder implements", expanded=True):
            code = run_agent(
                client, "Coder", "💻", coder_prompt,
                f"Implement the following design as Python code:\n\n{design}",
                coder_hist,
            )

        st.markdown('<div class="pipeline-arrow">↓</div>', unsafe_allow_html=True)

        with st.expander("🔍  Step 3 — Reviewer critiques", expanded=True):
            review = run_agent(
                client, "Reviewer", "🔍", reviewer_prompt,
                f"Review this Python code:\n\n{code}",
                reviewer_hist,
            )

        st.markdown('<div class="pipeline-arrow">↓</div>', unsafe_allow_html=True)

        with st.expander("✅  Step 4 — Coder revises", expanded=True):
            run_agent(
                client, "Coder (revised)", "✅", coder_prompt,
                (
                    "Here is a review of your code. Produce a corrected version "
                    "that addresses every issue.\n\n"
                    f"REVIEW:\n{review}\n\nORIGINAL CODE:\n{code}"
                ),
                coder_hist,
            )

        st.success("Pipeline complete! Final code is in Step 4.")


# ── Example: Research Team ────────────────────────────────────────────────────
elif "Research" in example:
    st.subheader("📊 Research Team")
    st.caption("3 specialist researchers explore a topic → Analyst extracts insights → Writer drafts report.")

    topic = st.text_input(
        "Research topic",
        value="the impact of large language models on software engineering workflows",
    )

    st.markdown("""
    **Pipeline:**  `TechResearcher` + `ImpactResearcher` + `FutureResearcher`  →  `Analyst`  →  `Writer`
    """)

    if st.button("▶  Run Research", type="primary", use_container_width=True):
        if not api_key:
            st.error("Enter your API key in the sidebar.")
            st.stop()

        client = anthropic.Anthropic(api_key=api_key)

        researchers = {
            "TechResearcher": (
                "🔬", "You are a technical research specialist. Surface important "
                "technical facts, tools, and architectural patterns. Use bullet points."
            ),
            "ImpactResearcher": (
                "🌍", "You are an industry impact researcher. Identify who is affected, "
                "workflow changes, case studies, and data. Use bullet points."
            ),
            "FutureResearcher": (
                "🔮", "You are a foresight researcher. Identify emerging trends, open "
                "questions, and risks on a 2-5 year horizon. Use bullet points."
            ),
        }

        st.divider()
        st.markdown("#### Phase 1 — Parallel Research")

        all_findings: dict[str, str] = {}
        for name, (icon, prompt) in researchers.items():
            hist: list = []
            with st.expander(f"{icon}  {name}", expanded=True):
                all_findings[name] = run_agent(
                    client, name, icon, prompt,
                    f"Research from your specialist perspective:\n\nTOPIC: {topic}",
                    hist,
                )

        st.markdown("#### Phase 2 — Analysis")
        combined = "\n\n".join(
            f"=== {n} ===\n{f}" for n, f in all_findings.items()
        )
        analyst_hist: list = []
        with st.expander("📈  Analyst — Key Insights", expanded=True):
            insights = run_agent(
                client, "Analyst", "📈",
                "You are a senior analyst. Distil 5-7 cross-cutting insights from "
                "research notes. Format: numbered list with bold headline + explanation.",
                f"Research notes on '{topic}':\n\n{combined}",
                analyst_hist,
            )

        st.markdown("#### Phase 3 — Report")
        writer_hist: list = []
        with st.expander("✍️  Writer — Final Report", expanded=True):
            run_agent(
                client, "Writer", "✍️",
                "You are a technology journalist. Write a clear, structured report "
                "with introduction, titled sections, and a forward-looking conclusion.",
                f"Write a report on '{topic}' based on:\n\n{insights}",
                writer_hist,
            )

        st.success("Research complete! Download or copy the report above.")


# ── Example: Earnings Analysis (Finance) ──────────────────────────────────────
elif "Earnings" in example:
    st.subheader("💰 Earnings Analysis — Asset Management")
    st.caption(
        "Paste an earnings call transcript or company description. "
        "Four specialist agents produce a full investment memo."
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        transcript = st.text_area(
            "Earnings call transcript / company description",
            placeholder=(
                "Paste the earnings call transcript here...\n\n"
                "Or describe the company and recent results, e.g.:\n"
                "'Apple Q4 2024: Revenue $94.9B (+6% YoY), iPhone revenue $46.2B, "
                "Services $24.9B (+12% YoY), gross margin 46.2%...'"
            ),
            height=200,
        )
    with col2:
        company = st.text_input("Company name", value="Apple")
        st.markdown("**Pipeline:**")
        st.markdown("1. 🔍 Researcher")
        st.markdown("2. 🐂 Bull Analyst")
        st.markdown("3. 🐻 Bear Analyst")
        st.markdown("4. ⚠️ Risk Manager")
        st.markdown("5. 📋 Report Writer")

    if st.button("▶  Analyse", type="primary", use_container_width=True):
        if not api_key:
            st.error("Enter your API key in the sidebar.")
            st.stop()
        if not transcript.strip():
            st.error("Please paste a transcript or company description.")
            st.stop()

        client = anthropic.Anthropic(api_key=api_key)

        st.divider()

        # Step 1 — Researcher
        researcher_hist: list = []
        with st.expander("🔍  Step 1 — Researcher extracts key facts", expanded=True):
            facts = run_agent(
                client, "Researcher", "🔍",
                (
                    "You are a financial research analyst. Given an earnings call "
                    "transcript or company description, extract and organise:\n"
                    "  • Revenue, earnings, margins (actuals vs expectations)\n"
                    "  • Management guidance and outlook\n"
                    "  • Key business segment performance\n"
                    "  • Notable quotes from management\n"
                    "  • Any surprises (positive or negative)\n"
                    "Use bullet points. Be specific with numbers."
                ),
                f"Extract key facts from this {company} earnings material:\n\n{transcript}",
                researcher_hist,
            )

        st.markdown('<div class="pipeline-arrow">↓</div>', unsafe_allow_html=True)

        # Step 2 — Bull Analyst
        bull_hist: list = []
        with st.expander("🐂  Step 2 — Bull Analyst — Why to BUY", expanded=True):
            bull_case = run_agent(
                client, "Bull Analyst", "🐂",
                (
                    "You are a bullish equity analyst. Given earnings facts, build "
                    "the strongest possible investment case FOR buying this stock. "
                    "Cover: growth catalysts, competitive moat, valuation support, "
                    "management quality. Use bullet points with specific evidence."
                ),
                f"Build the bull case for {company} based on:\n\n{facts}",
                bull_hist,
            )

        st.markdown('<div class="pipeline-arrow">↓</div>', unsafe_allow_html=True)

        # Step 3 — Bear Analyst
        bear_hist: list = []
        with st.expander("🐻  Step 3 — Bear Analyst — Why to SELL / AVOID", expanded=True):
            bear_case = run_agent(
                client, "Bear Analyst", "🐻",
                (
                    "You are a bearish equity analyst. Given earnings facts, build "
                    "the strongest possible case AGAINST this stock. Cover: risks, "
                    "decelerating growth, competition, valuation concerns, red flags "
                    "in management commentary. Use bullet points with evidence."
                ),
                f"Build the bear case for {company} based on:\n\n{facts}",
                bear_hist,
            )

        st.markdown('<div class="pipeline-arrow">↓</div>', unsafe_allow_html=True)

        # Step 4 — Risk Manager
        risk_hist: list = []
        with st.expander("⚠️  Step 4 — Risk Manager stress-tests the thesis", expanded=True):
            risk_assessment = run_agent(
                client, "Risk Manager", "⚠️",
                (
                    "You are a portfolio risk manager. Given bull and bear cases, "
                    "identify the top 5 risks that could invalidate the bull thesis, "
                    "assign each a likelihood (Low/Medium/High) and potential impact "
                    "(Low/Medium/High), and suggest how to monitor or hedge each risk."
                ),
                (
                    f"Stress-test the investment thesis for {company}.\n\n"
                    f"BULL CASE:\n{bull_case}\n\n"
                    f"BEAR CASE:\n{bear_case}"
                ),
                risk_hist,
            )

        st.markdown('<div class="pipeline-arrow">↓</div>', unsafe_allow_html=True)

        # Step 5 — Report Writer
        report_hist: list = []
        with st.expander("📋  Step 5 — Investment Memo", expanded=True):
            memo = run_agent(
                client, "Report Writer", "📋",
                (
                    "You are a senior portfolio manager writing an investment memo. "
                    "Structure your memo as:\n"
                    "  1. Executive Summary (Buy / Hold / Sell + 1 sentence rationale)\n"
                    "  2. Key Facts\n"
                    "  3. Bull Case\n"
                    "  4. Bear Case\n"
                    "  5. Key Risks\n"
                    "  6. Recommendation & Position Sizing\n"
                    "Be concise, direct, and actionable."
                ),
                (
                    f"Write an investment memo for {company}.\n\n"
                    f"FACTS:\n{facts}\n\n"
                    f"BULL CASE:\n{bull_case}\n\n"
                    f"BEAR CASE:\n{bear_case}\n\n"
                    f"RISKS:\n{risk_assessment}"
                ),
                report_hist,
            )

        st.success(f"✅ Investment memo for {company} complete!")

        # Download button
        st.download_button(
            label="⬇️  Download Memo as .txt",
            data=memo,
            file_name=f"{company}_investment_memo.txt",
            mime="text/plain",
        )
