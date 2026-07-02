# LangGraph / LangChain code skeletons (LangGraph 1.x, 2026)

Verify version-sensitive details against context7 `langgraph` — this API changes fast. (`InMemorySaver` is the current name; `MemorySaver` is the older alias.)

## StateGraph + reducers

```python
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated

class State(TypedDict):
    messages: Annotated[list, add_messages]      # merges by message id (no dupes)
    retry_count: int                              # plain value, last-write-wins

def call_llm(state: State) -> dict:
    return {"messages": [llm.invoke(state["messages"])]}

g = StateGraph(State)
g.add_node("llm", call_llm)
g.add_edge(START, "llm")
g.add_conditional_edges("llm", route_fn, {"tool": "tools", "done": END})
graph = g.compile(checkpointer=checkpointer)
```

`Command` to update state AND route in one return (replaces some conditional edges):

```python
from langgraph.types import Command
def node(state) -> Command:
    return Command(update={"retry_count": state["retry_count"] + 1}, goto="llm")
```

## Persistence / memory

```python
from langgraph.checkpoint.memory import InMemorySaver
# from langgraph.checkpoint.sqlite import SqliteSaver      # dev/test, durable
# from langgraph.checkpoint.postgres import PostgresSaver  # production

graph = g.compile(checkpointer=InMemorySaver())
cfg = {"configurable": {"thread_id": "user-123"}}          # scopes the conversation
graph.invoke({"messages": [("user", "hi")]}, cfg)
```

## Human-in-the-loop (checkpointer REQUIRED)

```python
from langgraph.types import interrupt, Command

def review(state):
    decision = interrupt({"draft": state["draft"]})        # pauses here
    return {"approved": decision["approved"]}

# ... later, after a human responds:
graph.invoke(Command(resume={"approved": True}), cfg)
```

## Streaming

```python
# Node-level updates as each node finishes (stable across versions):
for chunk in graph.stream({"messages": [...]}, cfg, stream_mode="updates"):
    print(chunk)                                   # {node_name: {state delta}}

# Token streaming from chat models inside the graph:
for token, meta in graph.stream({"messages": [...]}, cfg, stream_mode="messages"):
    print(token.content, end="", flush=True)
```

For fine-grained event streaming use `astream_events` — confirm the current `version=` and event shape via context7 (it changes between releases).

## Prebuilt ReAct agent

```python
from langgraph.prebuilt import create_react_agent
agent = create_react_agent(model=llm, tools=[search, calc],
                           prompt="You are a research specialist.",
                           checkpointer=InMemorySaver())
agent.invoke({"messages": [("user", "find X")]}, cfg)
```

## Tools + structured output

```python
llm_tools = llm.bind_tools([search_tool, calc_tool])

from pydantic import BaseModel
class Answer(BaseModel):
    reasoning: str
    value: float
structured = llm.with_structured_output(Answer)
structured.invoke("What is 2+2?")                  # -> Answer(...)
```

## Multi-agent — supervisor (prototyping)

```python
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent

researcher = create_react_agent(llm, tools=[web_search], name="researcher")
coder      = create_react_agent(llm, tools=[py_repl],    name="coder")
supervisor = create_supervisor(
    agents=[researcher, coder], model=llm,
    prompt="Route tasks; never do specialist work yourself. One specialist at a time.",
).compile()
```

For production, replace `create_supervisor` with a hand-built `StateGraph` whose routing node you own (state keys, failure exits). Set `recursion_limit` on `.compile()` / `.invoke()`.

## Fan-out with Send

```python
from langgraph.types import Send
def dispatch(state):
    return [Send("worker", {"item": x}) for x in state["items"]]
g.add_conditional_edges("splitter", dispatch)
```

## LCEL RAG (linear pipeline — no graph needed)

```python
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
rag = (RunnablePassthrough.assign(context=retriever | format_docs)
       | prompt | llm | StrOutputParser())
rag.invoke("What is X?")
```

## LangSmith eval

```python
from langsmith import Client
client = Client()
results = client.evaluate(
    lambda inputs: agent.invoke(inputs)["messages"],
    data="my_dataset",
    evaluators=[my_trajectory_judge],             # see `agentevals` package
)
```
