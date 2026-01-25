from typing import TypedDict, Optional

from langgraph.graph import StateGraph, END
from langchain_community.llms import Ollama


# -------------------------
# LLM setup
# -------------------------
llm = Ollama(model="mistral", temperature=0)


# -------------------------
# State
# -------------------------
class State(TypedDict):
    name: Optional[str]
    location: Optional[str]
    emergency_type: Optional[str]


# -------------------------
# Helper
# -------------------------
def llm_is_valid_emergency_type(value: str) -> bool:
    prompt = f"""
Is "{value}" one of these emergency types: fire, police, or ems?
Answer with ONLY 'YES' or 'NO'.
"""
    response = llm.invoke(prompt).strip().upper()
    return response.startswith("YES")


# -------------------------
# Intake Node (replaces fruit_node)
# -------------------------
def intake_node(state: State) -> State:
    print("📞 911 Intake\n")

    # Name
    name = input("What is your name? ").strip()

    # Location
    location = input("What is the emergency location? ").strip()

    # Emergency type (validated by LLM)
    while True:
        emergency_type = input("Is this Fire, Police, or EMS? ").strip().lower()

        if llm_is_valid_emergency_type(emergency_type):
            print(f"✅ Emergency type confirmed: {emergency_type}\n")
            break
        else:
            print("❌ Please enter one of: Fire, Police, or EMS.\n")

    return {
        "name": name,
        "location": location,
        "emergency_type": emergency_type,
    }


# -------------------------
# Routing after Intake
# -------------------------
def route_after_intake(state: State) -> str:
    etype = (state.get("emergency_type") or "").lower()

    if etype == "fire":
        return "fire"
    elif etype == "police":
        return "police"
    elif etype == "ems":
        return "ems"
    else:
        # Fallback safety
        return "police"


# -------------------------
# Fire Node
# -------------------------
def fire_node(state: State) -> State:
    print("🔥 FIRE DISPATCH\n")
    print(f"Caller:   {state['name']}")
    print(f"Location: {state['location']}\n")

    details = input("What is on fire? (house, car, bush, etc): ").strip()

    print("\n🚒 Fire details recorded.")
    print(f"Fire type: {details}\n")

    return state


# -------------------------
# Police Node
# -------------------------
def police_node(state: State) -> State:
    print("🚓 POLICE DISPATCH\n")
    print(f"Caller:   {state['name']}")
    print(f"Location: {state['location']}\n")

    details = input("What is happening? (theft, assault, suspicious, etc): ").strip()

    print("\n👮 Police details recorded.")
    print(f"Incident: {details}\n")

    return state


# -------------------------
# EMS Node
# -------------------------
def ems_node(state: State) -> State:
    print("🚑 EMS DISPATCH\n")
    print(f"Caller:   {state['name']}")
    print(f"Location: {state['location']}\n")

    details = input("What is the medical emergency? ").strip()

    print("\n🩺 EMS details recorded.")
    print(f"Medical issue: {details}\n")

    return state


# -------------------------
# Build Graph
# -------------------------
builder = StateGraph(State)

builder.add_node("intake", intake_node)
builder.add_node("fire", fire_node)
builder.add_node("police", police_node)
builder.add_node("ems", ems_node)

builder.set_entry_point("intake")

builder.add_conditional_edges(
    "intake",
    route_after_intake,
    {
        "fire": "fire",
        "police": "police",
        "ems": "ems",
    },
)

builder.add_edge("fire", END)
builder.add_edge("police", END)
builder.add_edge("ems", END)

graph = builder.compile()


# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    final_state = graph.invoke({
        "name": None,
        "location": None,
        "emergency_type": None,
    })

    print("📋 Final Call Summary")
    print(final_state)
