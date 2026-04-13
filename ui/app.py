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

from ui.pipelines import debate, code_review, research, finance, healthcare, small_business, retail, custom_builder

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
        "💬  Agent Debate",
        "🔧  Code Review",
        "📊  Research Team",
        "💰  Finance — Earnings Analysis",
        "🏥  Healthcare — Clinical Support",
        "💼  Small Business — Financial Review",
        "🛍️  Retail — Sales Intelligence",
        "🛠️  Custom Pipeline Builder",
    ], index=3)

    st.divider()
    st.caption("Each agent is a separate Claude instance with its own role and memory.")

# ── Main ──────────────────────────────────────────────────────────────────────
st.title("🤖 Multi-Agent AI Framework")

if not api_key:
    st.info("👈 Enter your Anthropic API key in the sidebar to get started.")
    st.stop()

client = anthropic.Anthropic(api_key=api_key)

if   "Debate"       in pipeline: debate.render(client)
elif "Code"         in pipeline: code_review.render(client)
elif "Research"     in pipeline: research.render(client)
elif "Finance"      in pipeline: finance.render(client)
elif "Healthcare"   in pipeline: healthcare.render(client)
elif "Small"        in pipeline: small_business.render(client)
elif "Retail"       in pipeline: retail.render(client)
elif "Custom"       in pipeline: custom_builder.render(client)
