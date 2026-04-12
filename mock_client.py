"""
mock_client.py — Drop-in replacement for anthropic.Anthropic client
====================================================================
Use this to test the multi-agent framework without any API calls or cost.

Usage:
    from mock_client import MockAnthropic
    client = MockAnthropic()          # instead of anthropic.Anthropic()
    # then pass client to agents/examples as normal
"""

import time
import random


MOCK_RESPONSES = {
    "default": "This is a mock response. The agent framework is working correctly. [MOCK]",
    "Researcher": "**Mock Research Summary** [MOCK]\n- Revenue: $94.9B (+6% YoY)\n- EPS: $1.64, beat by $0.04\n- Services: record $24.9B (+12%)\n- Gross margin: 46.2% (record)\n- Guidance: low-mid single digit growth",
    "BullAnalyst": "**Mock Bull Case** [MOCK]\n- Services flywheel accelerating (12% YoY)\n- Record gross margins signal pricing power\n- $156B cash enables continued buybacks\n- AI roadmap (Apple Intelligence) is a new catalyst",
    "BearAnalyst": "**Mock Bear Case** [MOCK]\n- China revenue declining (-1% YoY), Huawei competition\n- iPhone growth slowing (6% YoY, mature market)\n- Wearables declining (-3% YoY)\n- Valuation stretched at 30x earnings",
    "RiskManager": "**Mock Risk Assessment** [MOCK]\n1. China risk — High likelihood, High impact\n2. iPhone saturation — Medium/High\n3. Regulatory (App Store) — Medium/Medium\n4. AI execution risk — Low/High\n5. Macro slowdown — Medium/High",
    "ReportWriter": "**MOCK INVESTMENT MEMO** [MOCK]\n\n1. Executive Summary: HOLD — Strong fundamentals offset by China headwinds\n2. Key Facts: Revenue beat, record margins, Services momentum\n3. Bull Case: Services flywheel, AI optionality, capital returns\n4. Bear Case: China risk, iPhone maturity, stretched valuation\n5. Risks: Geopolitical, regulatory, macro\n6. Recommendation: 5% position, add on weakness below $220",
    "Optimist": "**Mock Optimist View** [MOCK]\nAI is an extraordinary creative amplifier. History shows technology always creates more jobs than it destroys. Humans + AI will achieve things neither could alone.",
    "Skeptic": "**Mock Skeptic View** [MOCK]\nThe scale of AI displacement is unprecedented. Creative fields face real disruption. We should proceed with caution and strong policy guardrails.",
    "Moderator": "**Mock Synthesis** [MOCK]\nBoth sides make valid points. AI will transform creative work — augmenting most roles while displacing some. The outcome depends heavily on policy and adoption pace.",
}


class MockMessage:
    """Mimics anthropic.types.Message"""
    def __init__(self, content_text, agent_name="default"):
        self.id = f"mock_msg_{random.randint(1000,9999)}"
        self.type = "message"
        self.role = "assistant"
        self.model = "mock-claude"
        self.stop_reason = "end_turn"
        self.stop_sequence = None
        self.usage = type("Usage", (), {"input_tokens": 100, "output_tokens": 50})()

        # Pick a relevant mock response
        response_text = MOCK_RESPONSES.get(agent_name, MOCK_RESPONSES["default"])
        self.content = [type("Block", (), {"type": "text", "text": response_text})()]


class MockMessages:
    """Mimics client.messages"""

    def create(self, model, max_tokens, system, messages, tools=None, thinking=None, **kwargs):
        # Infer agent name from system prompt keywords
        agent_name = "default"
        for name in MOCK_RESPONSES:
            if name.lower() in system.lower():
                agent_name = name
                break
        time.sleep(0.3)  # Simulate a tiny delay
        return MockMessage(content_text="", agent_name=agent_name)

    def stream(self, model, max_tokens, system, messages, tools=None, **kwargs):
        """Context manager that mimics streaming"""
        agent_name = "default"
        for name in MOCK_RESPONSES:
            if name.lower() in system.lower():
                agent_name = name
                break
        return MockStreamContext(agent_name)


class MockStreamContext:
    """Context manager mimicking client.messages.stream(...)"""
    def __init__(self, agent_name):
        self.agent_name = agent_name
        self._text = MOCK_RESPONSES.get(agent_name, MOCK_RESPONSES["default"])

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    @property
    def text_stream(self):
        """Yield words one at a time to simulate streaming"""
        for word in self._text.split():
            time.sleep(0.05)
            yield word + " "


class MockAnthropic:
    """Drop-in replacement for anthropic.Anthropic()"""
    def __init__(self, api_key=None, **kwargs):
        self.messages = MockMessages()
        print("[MockAnthropic] Running in MOCK mode — no API calls, no cost.")


# ── Quick test ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from agents import Agent, Orchestrator

    client = MockAnthropic()

    researcher = Agent("Researcher", "You are a financial researcher.", client)
    bull = Agent("BullAnalyst", "You are a bull analyst.", client)

    orch = Orchestrator(verbose=True)
    orch.register(researcher).register(bull)

    facts = orch.send("Researcher", "Summarise Apple Q4 2024", from_name="User")
    print("\n--- Facts ---\n", facts)

    bull_case = orch.send("BullAnalyst", f"Build bull case from:\n{facts}", from_name="Researcher")
    print("\n--- Bull Case ---\n", bull_case)

    orch.print_log()
    print("\nAll done — zero API cost!")
