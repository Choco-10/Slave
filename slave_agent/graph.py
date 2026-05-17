from langgraph.graph import StateGraph, END
from typing import TypedDict
from slave_agent.agents import planner, scaffolder, writer, critic


class State(TypedDict, total=False):
    task: str
    stack: str
    plan: str
    filetree: str
    files_blob: str
    review: str
    iterations: int
    next: str


MAX_ITER = 2


# ---------------- MANAGER ----------------
def manager(state: State):
    iterations = state.get("iterations", 0)

    if iterations >= MAX_ITER:
        return {"next": "end"}

    if not state.get("plan"):
        return {"next": "planner"}

    if not state.get("filetree"):
        return {"next": "scaffolder"}

    if not state.get("files_blob"):
        return {"next": "writer"}

    if not state.get("review"):
        return {"next": "critic"}

    review = state.get("review", "").strip().upper()

    if "FIX" in review:
        return {
            "next": "writer",
            "iterations": iterations + 1,
            # Force writer output to be re-reviewed before another rewrite.
            "review": "",
        }

    return {"next": "end"}


def route(state: State):
    return state["next"]


# ---------------- GRAPH ----------------
graph = StateGraph(State)

graph.add_node("manager", manager)
graph.add_node("planner", planner)
graph.add_node("scaffolder", scaffolder)
graph.add_node("writer", writer)
graph.add_node("critic", critic)

graph.set_entry_point("manager")

graph.add_conditional_edges(
    "manager",
    route,
    {
        "planner": "planner",
        "scaffolder": "scaffolder",
        "writer": "writer",
        "critic": "critic",
        "end": END,
    },
)

graph.add_edge("planner", "manager")
graph.add_edge("scaffolder", "manager")
graph.add_edge("writer", "manager")
graph.add_edge("critic", "manager")

app = graph.compile()