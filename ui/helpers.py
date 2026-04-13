"""Shared helpers for all pipeline UIs."""
import anthropic
import streamlit as st


def stream_agent(client, system_prompt, messages, model="claude-haiku-4-5-20251001", max_tokens=4096):
    with client.messages.stream(
        model=model, max_tokens=max_tokens, system=system_prompt, messages=messages,
    ) as stream:
        for text in stream.text_stream:
            yield text


def run_agent(client, name, icon, system_prompt, user_message, history, model="claude-haiku-4-5-20251001"):
    st.markdown(f'<div class="agent-label">{icon} {name}</div>', unsafe_allow_html=True)
    history.append({"role": "user", "content": user_message})
    full_response = st.write_stream(stream_agent(client, system_prompt, history, model))
    history.append({"role": "assistant", "content": full_response})
    return full_response
