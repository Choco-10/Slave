import ollama
from langgraph.graph import StateGraph, END
from typing import TypedDict


# ----------------------------
# STATE (shared memory)
# ----------------------------
class AgentState(TypedDict):
    task: str
    language: str
    plan: str
    code: str
    review: str
    next: str

# ----------------------------
# MODELS
# ----------------------------
PLANNER_MODEL = "qwen2.5:7b"
CODER_MODEL = "deepseek-coder:6.7b"
CRITIC_MODEL = "qwen2.5:7b"


# ----------------------------
# AGENTS
# ----------------------------

def manager(state: AgentState):
    res = ollama.chat(
        model="qwen2.5:7b",
        messages=[{
            "role": "user",
            "content": f"""
You are a workflow manager for a coding agent system.

Task: {state['task']}
Language: {state['language']}

Current state:
Plan: {state['plan']}
Code: {state['code']}
Review: {state['review']}

Decide the next step.

Options:
- planner
- coder
- critic
- end

Rules:
- If no plan exists → planner
- If no code exists → coder
- If review says issues → coder
- If code is good → end

Return ONLY one word.
"""
        }]
    )

    decision = res["message"]["content"].strip().lower()
    return {"next": decision}


def planner(state: AgentState):
    res = ollama.chat(
        model=PLANNER_MODEL,
        messages=[{
            "role": "user",
            "content": f"""
Task: {state['task']}
Language: {state['language']}

Break into steps.
"""
        }]
    )

    return {
        "plan": res["message"]["content"],
        "next": "coder"
    }


def coder(state: AgentState):
    res = ollama.chat(
        model=CODER_MODEL,
        messages=[{
            "role": "user",
            "content": f"""
Language: {state['language']}
Plan:
{state['plan']}

Write complete code.
"""
        }]
    )

    return {
        "code": res["message"]["content"],
        "next": "critic"
    }


def critic(state: AgentState):
    res = ollama.chat(
        model=CRITIC_MODEL,
        messages=[{
            "role": "user",
            "content": f"""
Language: {state['language']}

Code:
{state['code']}

Review it and identify issues.
"""
        }]
    )

    return {
        "review": res["message"]["content"],
        "next": "manager"
    }


# ----------------------------
# ROUTER (simple decision logic)
# ----------------------------
def route(state: AgentState):
    return state["next"]


# ----------------------------
# BUILD GRAPH
# ----------------------------
graph = StateGraph(AgentState)

graph.add_node("planner", planner)
graph.add_node("coder", coder)
graph.add_node("critic", critic)
graph.add_node("manager", manager)

graph.set_entry_point("manager")

graph.add_conditional_edges(
    "manager",
    route,
    {
        "planner": "planner",
        "coder": "coder",
        "critic": "critic",
        "end": END
    }
)

graph.add_edge("planner", "manager")
graph.add_edge("coder", "manager")
graph.add_edge("critic", "manager")

app = graph.compile()