---
name: langchain-stack
description: Use when building agentic or LLM-pipeline code with LangChain or LangGraph — StateGraph, nodes/edges, state reducers, checkpointers/memory/persistence, tool calling, structured output, streaming, human-in-the-loop/interrupts, multi-agent supervisor or swarm, LangSmith eval/tracing, or migrating legacy chains/AgentExecutor to LangGraph. Reflects the LangGraph 1.x API (late 2025/2026); verify version-sensitive calls via context7.
---

# LangChain / LangGraph stack (current)

## Overview

**LCEL (`|` Runnables) for linear pipelines; LangGraph for anything stateful, cyclical, or agentic.** The legacy `AgentExecutor`/`initialize_agent`/`*Chain` layer is deprecated — new code uses `create_react_agent` or a hand-built `StateGraph`. Always verify the exact API against current docs (context7 `langgraph`/`langchain`); this ecosystem moves faster than any training cutoff.

## When to use

- Building an agent, tool-calling loop, RAG pipeline, or multi-agent system in Python.
- Working with `StateGraph`, reducers, checkpointers/memory, streaming, interrupts/human-in-the-loop.
- Migrating old `AgentExecutor`/`LLMChain`/`RetrievalQA` code.
- Wiring LangSmith tracing/eval.

**Not for:** non-LangChain LLM calls or prompt design → use the Anthropic SDK / `senior-prompt-engineer`. Data modeling → `senior-data-scientist`.

## Current vs deprecated (mid-2026)

| Legacy (avoid) | Use instead |
|---|---|
| `AgentExecutor`, `initialize_agent` | `create_react_agent` (langgraph.prebuilt) or custom `StateGraph` |
| `ZeroShotAgent`, `ReActAgent` | `create_react_agent` |
| `LLMChain` | LCEL pipe: `prompt \| llm \| parser` |
| `RetrievalQA`, `ConversationalRetrievalChain` | LCEL RAG chain / LangGraph retriever node |
| `stream_events(version="v1"/"v2")` | `stream_events(..., version="v3")` |
| old `breakpoint` HITL | `interrupt()` + `Command(resume=...)` |
| `LANGCHAIN_TRACING_V2` env | `LANGSMITH_TRACING=true` |

## Canonical patterns (quick reference)

- **Graph:** `StateGraph(State)` → `add_node` / `add_edge` / `add_conditional_edges` → `.compile(checkpointer=...)`.
- **State:** `TypedDict` with `Annotated[list, add_messages]` for messages (dedups by ID); `operator.add` to append generic lists. `create_agent` factory needs `TypedDict` (not Pydantic).
- **Routing + update in one return:** `Command(update={...}, goto="node")`; `Command(goto=..., graph=Command.PARENT)` from a subgraph.
- **Persistence:** compile with `InMemorySaver` (dev) / `SqliteSaver` / `PostgresSaver`; scope a conversation with `config={"configurable": {"thread_id": "..."}}`.
- **Human-in-the-loop:** `interrupt(payload)` pauses; resume with `graph.invoke(Command(resume=value), config)`. **A checkpointer is mandatory** or it silently won't pause.
- **Streaming:** `graph.stream(input, config, stream_mode="updates"|"messages"|"values")` (event-level: `astream_events` — confirm current `version=` via context7).
- **Prebuilt agent:** `create_react_agent(model, tools, prompt=..., checkpointer=...)`.
- **Multi-agent:** `langgraph-supervisor` (`create_supervisor`) or `langgraph-swarm` for prototyping; own a manual `StateGraph` for production. Always set `recursion_limit`.
- **Structured output:** `llm.with_structured_output(PydanticModel)`; tools via `llm.bind_tools([...])`.

Full code skeletons: see `patterns.md`.

## LangSmith eval

Set `LANGSMITH_TRACING=true` + `LANGSMITH_API_KEY` → runs auto-trace, no code change. Loop: run → traces in UI → annotate failures into a dataset → `client.evaluate(fn, data=..., evaluators=[...])` → compare experiments. The `agentevals` package adds trajectory/tool-call judges.

## Common mistakes

- **`AgentExecutor` in new code** — deprecated; use `create_react_agent` or `StateGraph`.
- **`interrupt()` without a checkpointer** — the graph never pauses; compile with one.
- **`operator.add` for message lists** — blind append duplicates on manual `update_state`; use `add_messages`.
- **Mutual handoffs (swarm) without `recursion_limit`** — infinite loop until budget death. Set `recursion_limit=25`.
- **Reordering `@task`/`interrupt()` before a resume** in the functional API — results are replayed by position; reordering corrupts the replay.
- **`stream_events` v1/v2** — deprecated; use `version="v3"`.
