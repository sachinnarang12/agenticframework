"""
Orchestrator — coordinates multiple agents.

The Orchestrator is the glue layer between agents. It handles:
- Agent registration and lookup
- Message routing between agents
- Sequential pipelines (output of one → input of next)
- Broadcast (send same message to all agents)
- Message logging for observability
"""

from typing import Optional
from .base import Agent


class Orchestrator:
    """
    Coordinates a collection of named agents.

    Interaction patterns supported:
    1. Direct routing  — send a message to a specific agent
    2. Pipeline        — chain agents so each agent's output feeds the next
    3. Broadcast       — send the same message to all agents, collect responses
    4. Feedback loop   — two agents critique each other for N rounds
    """

    def __init__(self, verbose: bool = True):
        self.agents: dict[str, Agent] = {}
        self.message_log: list[dict] = []
        self.verbose = verbose

    # ------------------------------------------------------------------
    # Agent management
    # ------------------------------------------------------------------

    def register(self, agent: Agent) -> "Orchestrator":
        """Register an agent. Returns self for chaining."""
        self.agents[agent.name] = agent
        if self.verbose:
            print(f"[Orchestrator] Registered agent: {agent.name}")
        return self

    def list_agents(self) -> list[str]:
        """Return names of all registered agents."""
        return list(self.agents.keys())

    # ------------------------------------------------------------------
    # Routing
    # ------------------------------------------------------------------

    def send(
        self,
        to: str,
        message: str,
        from_name: str = "user",
        stream: bool = True,
        use_thinking: bool = False,
    ) -> str:
        """
        Send a message to a named agent and return its response.

        Args:
            to: Name of the target agent.
            message: The message content.
            from_name: Label for the sender (used in logs).
            stream: If True, stream response tokens to stdout.
            use_thinking: Enable adaptive thinking on the target agent.

        Returns:
            The agent's response text.
        """
        if to not in self.agents:
            raise ValueError(
                f"Agent '{to}' not found. Registered: {self.list_agents()}"
            )

        self._log(from_name, to, message)

        if self.verbose:
            print(f"\n{'─' * 60}")
            print(f"  {from_name}  →  {to}")
            print(f"{'─' * 60}")

        agent = self.agents[to]
        if stream:
            response = agent.stream_chat(message, print_output=self.verbose)
        else:
            response = agent.chat(message, use_thinking=use_thinking)
            if self.verbose:
                print(response)

        return response

    # ------------------------------------------------------------------
    # Interaction patterns
    # ------------------------------------------------------------------

    def pipeline(
        self,
        steps: list[tuple[str, str]],
        initial_input: str,
        stream: bool = True,
    ) -> str:
        """
        Run agents in a sequential pipeline.

        Each step is (agent_name, message_template). The template may use
        {input} or {previous} which will be substituted with the prior step's
        output. The first step uses `initial_input` directly.

        Args:
            steps: List of (agent_name, message_template) tuples.
            initial_input: The starting message / user request.
            stream: Stream agent responses to stdout.

        Returns:
            The final agent's response.

        Example:
            orchestrator.pipeline(
                steps=[
                    ("planner",  "Plan how to build: {input}"),
                    ("coder",    "Implement this plan:\n{previous}"),
                    ("reviewer", "Review this code:\n{previous}"),
                ],
                initial_input="a calculator API",
            )
        """
        current = initial_input
        print(f"\n{'=' * 60}")
        print(f"PIPELINE START  ({len(steps)} steps)")
        print(f"{'=' * 60}")

        for i, (agent_name, template) in enumerate(steps, 1):
            print(f"\n[Step {i}/{len(steps)}]")
            message = template.format(input=current, previous=current)
            current = self.send(agent_name, message, stream=stream)

        print(f"\n{'=' * 60}")
        print("PIPELINE COMPLETE")
        print(f"{'=' * 60}\n")
        return current

    def feedback_loop(
        self,
        agent_a: str,
        agent_b: str,
        initial_message: str,
        rounds: int = 2,
        stream: bool = True,
    ) -> tuple[str, str]:
        """
        Run a feedback loop between two agents.

        Agent A produces output → Agent B critiques it → Agent A revises →
        Agent B re-critiques → … for `rounds` iterations.

        Args:
            agent_a: Name of the producing agent.
            agent_b: Name of the critiquing agent.
            initial_message: The starting prompt for Agent A.
            rounds: Number of critique-revise cycles.
            stream: Stream responses to stdout.

        Returns:
            (final_a_response, final_b_response) tuple.
        """
        print(f"\n{'=' * 60}")
        print(f"FEEDBACK LOOP  ({rounds} rounds)  {agent_a} ↔ {agent_b}")
        print(f"{'=' * 60}")

        # Agent A produces initial output
        a_response = self.send(agent_a, initial_message, stream=stream)
        b_response = ""

        for round_num in range(1, rounds + 1):
            print(f"\n[Round {round_num}/{rounds}]")

            # Agent B critiques
            b_response = self.send(
                agent_b,
                f"Please critique and suggest improvements:\n\n{a_response}",
                from_name=agent_a,
                stream=stream,
            )

            # Agent A revises (except after the last round)
            if round_num < rounds:
                a_response = self.send(
                    agent_a,
                    f"Here is feedback on your previous response. Please revise:\n\n{b_response}",
                    from_name=agent_b,
                    stream=stream,
                )

        print(f"\n{'=' * 60}")
        print("FEEDBACK LOOP COMPLETE")
        print(f"{'=' * 60}\n")
        return a_response, b_response

    def broadcast(
        self,
        message: str,
        stream: bool = False,
    ) -> dict[str, str]:
        """
        Send the same message to all registered agents.

        Args:
            message: The message to broadcast.
            stream: Stream each response.

        Returns:
            Dict mapping agent_name → response.
        """
        print(f"\n{'=' * 60}")
        print(f"BROADCAST  (to {len(self.agents)} agents)")
        print(f"{'=' * 60}")

        responses: dict[str, str] = {}
        for name in self.agents:
            responses[name] = self.send(name, message, stream=stream)
        return responses

    # ------------------------------------------------------------------
    # Observability
    # ------------------------------------------------------------------

    def print_log(self) -> None:
        """Print the full message routing log."""
        print(f"\n{'=' * 60}")
        print("MESSAGE LOG")
        print(f"{'=' * 60}")
        for entry in self.message_log:
            snippet = entry["message"][:80].replace("\n", " ")
            if len(entry["message"]) > 80:
                snippet += "…"
            print(f"  [{entry['from']}] → [{entry['to']}]: {snippet}")
        print()

    def reset_all(self) -> None:
        """Reset conversation history for all agents."""
        for agent in self.agents.values():
            agent.reset()
        self.message_log.clear()
        print("[Orchestrator] All agents reset.")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _log(self, from_name: str, to: str, message: str) -> None:
        self.message_log.append({
            "from": from_name,
            "to": to,
            "message": message,
        })

    def __repr__(self) -> str:
        return f"Orchestrator(agents={self.list_agents()})"
