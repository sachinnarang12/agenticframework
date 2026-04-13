"""Custom Pipeline Builder — create your own agents from the UI."""
import streamlit as st
from ui.helpers import run_agent

ICONS = ["🤖","🔍","📊","💡","✍️","⚙️","🎯","🧠","🔬","📋","⚠️","💰","🏥","🛍️","💼"]


def render(client):
    st.subheader("🛠️ Custom Pipeline Builder")
    st.caption("Define your own agents and run them as a sequential pipeline.")

    # Initialise session state
    if "custom_agents" not in st.session_state:
        st.session_state.custom_agents = [
            {"name": "Agent 1", "icon": "🤖", "prompt": "You are a helpful assistant. Summarise the input clearly."},
            {"name": "Agent 2", "icon": "✍️", "prompt": "You are a writer. Take the summary and expand it into a polished report."},
        ]

    st.markdown("#### 1. Define Your Agents")
    st.caption("Each agent receives the previous agent's output as its input.")

    agents = st.session_state.custom_agents
    to_delete = None

    for i, agent in enumerate(agents):
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 3, 1])
            with c1:
                agent["icon"] = st.selectbox("Icon", ICONS,
                    index=ICONS.index(agent["icon"]) if agent["icon"] in ICONS else 0,
                    key=f"icon_{i}")
                agent["name"] = st.text_input("Name", value=agent["name"], key=f"name_{i}")
            with c2:
                agent["prompt"] = st.text_area("System prompt (this agent's role & instructions)",
                    value=agent["prompt"], height=100, key=f"prompt_{i}")
            with c3:
                st.markdown("<br><br>", unsafe_allow_html=True)
                if len(agents) > 1 and st.button("🗑️ Remove", key=f"del_{i}"):
                    to_delete = i

            if i < len(agents) - 1:
                st.markdown('<div style="text-align:center;color:#6b7280;font-size:20px">↓</div>',
                    unsafe_allow_html=True)

    if to_delete is not None:
        st.session_state.custom_agents.pop(to_delete)
        st.rerun()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Add Agent", use_container_width=True):
            n = len(agents) + 1
            st.session_state.custom_agents.append(
                {"name": f"Agent {n}", "icon": "🤖", "prompt": f"You are agent {n}. Process the input and produce your output."})
            st.rerun()
    with col2:
        if st.button("🔄 Reset to Default", use_container_width=True):
            del st.session_state.custom_agents
            st.rerun()

    st.divider()
    st.markdown("#### 2. Enter Your Input")
    user_input = st.text_area("Initial input for the first agent",
        placeholder="Paste your data, question, or content here...", height=150)

    st.divider()
    st.markdown("#### 3. Run Pipeline")
    st.markdown(f"**{len(agents)} agent(s):** " + " → ".join(f"{a['icon']} {a['name']}" for a in agents))

    if st.button("▶  Run Custom Pipeline", type="primary", use_container_width=True):
        if not user_input.strip():
            st.error("Please enter some input for the pipeline.")
            st.stop()
        if not any(a["prompt"].strip() for a in agents):
            st.error("Please add at least one agent with a system prompt.")
            st.stop()

        st.divider()
        st.markdown("#### Results")

        current_input = user_input
        final_output = ""

        for i, agent in enumerate(agents):
            hist: list = []
            label = f"Step {i+1} — {agent['icon']} {agent['name']}"
            with st.expander(label, expanded=True):
                if i == 0:
                    msg = current_input
                else:
                    msg = f"Here is the output from the previous step:\n\n{current_input}"

                output = run_agent(client, agent["name"], agent["icon"],
                    agent["prompt"], msg, hist)
                current_input = output
                final_output = output

        st.success("✅ Pipeline complete!")
        st.download_button("⬇️ Download Final Output", data=final_output,
            file_name="custom_pipeline_output.txt", mime="text/plain")
