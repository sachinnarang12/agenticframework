"""
Base Agent class for multi-agent interactions.

Each Agent wraps a Claude model instance with a specific role (system prompt)
and maintains its own conversation history, enabling stateful multi-turn dialogue.
"""

import anthropic
from typing import Optional


class Agent:
    """
    A single AI agent powered by Claude.

    Agents have:
    - A name (used for routing and display)
    - A role / system prompt (defines the agent's persona and expertise)
    - A conversation history (agents remember prior turns)
    - Optional tools (for agents that need to take actions)
    """

    def __init__(
        self,
        name: str,
        system_prompt: str,
        client: anthropic.Anthropic,
        model: str = "claude-haiku-4-5-20251001",
        tools: Optional[list] = None,
    ):
        self.name = name
        self.system_prompt = system_prompt
        self.client = client
        self.model = model
        self.tools = tools or []
        self.messages: list[dict] = []

    def chat(
        self,
        user_message: str,
        use_thinking: bool = False,
        max_tokens: int = 4096,
    ) -> str:
        """
        Send a message to this agent and get a response.

        Args:
            user_message: The message to send.
            use_thinking: Enable adaptive thinking for complex reasoning tasks.
            max_tokens: Maximum tokens in the response.

        Returns:
            The agent's text response.
        """
        self.messages.append({"role": "user", "content": user_message})

        kwargs: dict = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": self.system_prompt,
            "messages": self.messages,
        }

        if use_thinking:
            kwargs["thinking"] = {"type": "adaptive"}
            kwargs["max_tokens"] = max(max_tokens, 8192)

        if self.tools:
            kwargs["tools"] = self.tools

        response = self.client.messages.create(**kwargs)

        # Handle tool-use loop automatically
        while response.stop_reason == "tool_use":
            tool_results = self._execute_tools(response.content)
            self.messages.append({"role": "assistant", "content": response.content})
            self.messages.append({"role": "user", "content": tool_results})
            response = self.client.messages.create(**kwargs)

        text = next(
            (block.text for block in response.content if block.type == "text"), ""
        )

        # Store the assistant turn (use content list if tools are involved)
        if self.tools:
            self.messages.append({"role": "assistant", "content": response.content})
        else:
            self.messages.append({"role": "assistant", "content": text})

        return text

    def stream_chat(
        self,
        user_message: str,
        print_output: bool = True,
        max_tokens: int = 8192,
    ) -> str:
        """
        Stream a response token-by-token and return the full text.

        Args:
            user_message: The message to send.
            print_output: Whether to print tokens as they stream.
            max_tokens: Maximum tokens in the response.

        Returns:
            The full response text.
        """
        self.messages.append({"role": "user", "content": user_message})

        full_text = ""
        with self.client.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            system=self.system_prompt,
            messages=self.messages,
        ) as stream:
            for text in stream.text_stream:
                if print_output:
                    print(text, end="", flush=True)
                full_text += text

        if print_output:
            print()  # newline after stream ends

        self.messages.append({"role": "assistant", "content": full_text})
        return full_text

    def reset(self) -> None:
        """Clear the agent's conversation history."""
        self.messages = []

    def _execute_tools(self, content_blocks: list) -> list:
        """
        Execute tool calls found in a response.
        Override this method to implement custom tool execution logic.

        Returns a list of tool_result content blocks.
        """
        results = []
        for block in content_blocks:
            if block.type == "tool_use":
                # Default: return a placeholder. Override in subclasses.
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": f"Tool '{block.name}' executed (no handler registered).",
                })
        return results

    def inject_message(self, role: str, content: str) -> None:
        """
        Inject a message directly into history without calling the API.
        Useful for seeding an agent with context from another agent.

        Args:
            role: "user" or "assistant"
            content: The message content.
        """
        self.messages.append({"role": role, "content": content})

    def __repr__(self) -> str:
        return (
            f"Agent(name='{self.name}', model='{self.model}', "
            f"turns={len(self.messages) // 2})"
        )
