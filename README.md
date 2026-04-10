# Multi-Agent Interaction Framework

An example project demonstrating how to build and coordinate multiple AI agents using the [Anthropic Claude API](https://platform.claude.com/docs). Includes three runnable patterns and a deployment guide for [Anthropic Agent Core (Managed Agents)](https://platform.claude.com/docs/en/managed-agents/overview.md).

---

## What's inside

```
agenticframework/
├── agents/
│   ├── base.py          # Agent — wraps a Claude model with a role & history
│   └── orchestrator.py  # Orchestrator — routes messages between agents
├── examples/
│   ├── 01_two_agent_debate.py   # Peer-to-peer: Optimist ↔ Skeptic + Moderator
│   ├── 02_code_pipeline.py      # Pipeline: Architect → Coder → Reviewer → Coder
│   └── 03_research_team.py      # Parallel + synthesis: 3 Researchers → Analyst → Writer
├── managed_agents/
│   ├── setup.py         # ONE-TIME: create Agent objects on Agent Core
│   └── run_session.py   # RUNTIME: run the pipeline via hosted sessions
├── main.py              # Interactive menu / CLI entry point
├── requirements.txt
└── .env.example
```

---

## Quick start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set your API key

```bash
cp .env.example .env
# Edit .env and add your key:
#   ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Run an example

```bash
# Interactive menu
python main.py

# Or pick one directly
python main.py --example 1   # Two-agent debate
python main.py --example 2   # Code review pipeline
python main.py --example 3   # Research team
```

---

## The three interaction patterns

### Pattern 1 — Peer-to-peer debate (`01_two_agent_debate.py`)

```
Optimist ←→ Skeptic   (N rounds)
               ↓
           Moderator  (synthesis)
```

Two agents with opposing personas debate a topic. A third agent synthesises a balanced conclusion. Shows how agent output becomes another agent's input in a conversational loop.

---

### Pattern 2 — Sequential pipeline (`02_code_pipeline.py`)

```
User task
   → Architect  (design plan)
   → Coder      (implementation)
   → Reviewer   (code review)
   → Coder      (revised code)
```

Each agent's output is the next agent's input. The Coder agent sees its own prior output alongside the Reviewer's feedback when revising — demonstrating agents that maintain context across multiple turns.

---

### Pattern 3 — Parallel broadcast + synthesis (`03_research_team.py`)

```
Topic ──┬─→ TechResearcher   ─┐
        ├─→ ImpactResearcher  ─┼─→ Analyst → Writer
        └─→ FutureResearcher  ─┘
```

Three specialist researchers work the same topic from different angles simultaneously. Their findings are merged and fed to an Analyst, who distils key insights, then a Writer produces a polished report.

---

## Core abstractions

### `Agent` (`agents/base.py`)

```python
agent = Agent(
    name="Reviewer",
    system_prompt="You are a code reviewer…",
    client=anthropic.Anthropic(),
    model="claude-opus-4-6",   # default
)

# Single-shot response
reply = agent.chat("Review this function: …")

# Streaming response (prints tokens as they arrive)
reply = agent.stream_chat("Review this function: …")

# Agents are stateful — they remember conversation history
agent.reset()   # clear history
```

### `Orchestrator` (`agents/orchestrator.py`)

```python
orch = Orchestrator()
orch.register(architect).register(coder).register(reviewer)

# Route a single message
response = orch.send(to="Architect", message="Design a cache")

# Sequential pipeline
final = orch.pipeline(
    steps=[
        ("Architect", "Design: {input}"),
        ("Coder",     "Implement:\n{previous}"),
        ("Reviewer",  "Review:\n{previous}"),
    ],
    initial_input="a thread-safe LRU cache",
)

# Critic ↔ Creator feedback loop
orch.feedback_loop("Coder", "Reviewer", initial_message="Write a binary search", rounds=2)

# Broadcast to all agents
orch.broadcast("Summarise your role in one sentence.")
```

---

## Deploying on Agent Core (Managed Agents)

Agent Core hosts each agent as a versioned object and provisions an isolated container per session. All the local patterns above translate directly.

### Step 1 — One-time setup (run once, save the IDs)

```bash
python managed_agents/setup.py
```

This creates:
- A cloud **Environment** (container template)
- Three **Agents** (Architect, Coder, Reviewer) with your system prompts

Copy the printed IDs into `.env`:

```
AGENT_CORE_ENV_ID=env_...
AGENT_ARCHITECT_ID=agent_...
AGENT_ARCHITECT_VERSION=...
AGENT_CODER_ID=agent_...
AGENT_CODER_VERSION=...
AGENT_REVIEWER_ID=agent_...
AGENT_REVIEWER_VERSION=...
```

### Step 2 — Run a pipeline session (every invocation)

```bash
python managed_agents/run_session.py
```

Each pipeline step:
1. Creates a fresh **Session** pinned to the pre-created agent
2. Opens an SSE event stream
3. Sends the user message
4. Streams the agent's response token-by-token
5. Archives the session when done

The output of each session is passed as input to the next — same pipeline logic as the local examples, but running on Anthropic's hosted infrastructure.

### Key concepts

| Concept | What it is |
|---|---|
| **Agent** | Persistent, versioned config: model + system prompt + tools. Create once. |
| **Environment** | Container template (networking, packages). Reusable across agents. |
| **Session** | One run of an agent inside an environment. Stateful, ephemeral. |
| **Event stream** | SSE stream of `agent.message`, `session.status_idle`, etc. |

> **Note**: Never call `agents.create()` in your hot path. Create agents once in setup, then reference them by ID.

---

## Customising

- **Swap the model**: Change `model="claude-haiku-4-5"` on any agent for faster/cheaper runs.
- **Enable thinking**: Pass `use_thinking=True` to `agent.chat()` for complex reasoning tasks.
- **Add tools**: Provide a `tools=[...]` list to `Agent(...)` to give an agent web search, code execution, etc.
- **Change the topic/task**: Edit the `TOPIC` / `TASK` constants at the top of each example file.

---

## Requirements

- Python 3.10+
- `anthropic >= 0.52.0`
- An Anthropic API key with access to `claude-opus-4-6`
- For Agent Core: access to the Managed Agents beta
