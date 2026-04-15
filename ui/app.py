"""
Multi-Agent AI Framework — Streamlit UI
========================================
Run:  streamlit run ui/app.py
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import anthropic
import streamlit as st

from ui.pipelines import debate, code_review, research, finance, healthcare, small_business, retail, custom_builder, wannaeat, ma_migration

st.set_page_config(page_title="Multi-Agent AI Framework", page_icon="🤖",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.agent-label {
    font-size:13px; font-weight:700; text-transform:uppercase;
    letter-spacing:1px; color:#a78bfa; margin-bottom:6px;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🤖 Multi-Agent AI")
    st.caption("Powered by Claude Haiku")
    st.divider()

    api_key = st.text_input("Anthropic API Key", type="password",
        placeholder="sk-ant-...", help="Get your key at console.anthropic.com")
    st.divider()

    pipeline = st.radio("Choose a pipeline", options=[
        "🍽️  WannaEat — Catering Proposal",
        "🔄  M&A — Systems Migration",
        "💰  Finance — Earnings Analysis",
        "🏥  Healthcare — Clinical Support",
        "💼  Small Business — Financial Review",
        "🛍️  Retail — Sales Intelligence",
        "🛠️  Custom Pipeline Builder",
        "💬  Agent Debate",
        "🔧  Code Review",
        "📊  Research Team",
    ], index=0)

    st.divider()
    st.caption("Each agent is a separate Claude instance with its own role and memory.")

# ── Main ──────────────────────────────────────────────────────────────────────
st.title("🤖 Multi-Agent AI Framework")

if not api_key:
    st.info("👈 Enter your Anthropic API key in the sidebar to get started.")
    st.stop()

client = anthropic.Anthropic(api_key=api_key)

if   "WannaEat"     in pipeline: wannaeat.render(client)
elif "M&A"          in pipeline: ma_migration.render(client)
elif "Finance"      in pipeline: finance.render(client)
elif "Healthcare"   in pipeline: healthcare.render(client)
elif "Small"        in pipeline: small_business.render(client)
elif "Retail"       in pipeline: retail.render(client)
elif "Custom"       in pipeline: custom_builder.render(client)
elif "Debate"       in pipeline: debate.render(client)
elif "Code"         in pipeline: code_review.render(client)
elif "Research"     in pipeline: research.render(client)
