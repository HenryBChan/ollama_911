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
    fruit: Optional[str]
    color: Optional[str]
    animal: Optional[str]


# -------------------------
# Helper
# -------------------------
def llm_is_valid(prompt: str) -> bool:
    response = llm.invoke(prompt).strip().upper()
    return response.startswith("YES")


# -------------------------
# Fruit Node
# -------------------------
def fruit_node(state: State) -> State:
    while True:
        user_input = input("🍎 Enter a fruit: ").strip().lower()

        prompt = f"""
Is "{user_input}" a fruit?
Answer with ONLY 'YES' or 'NO'.
"""
        if llm_is_valid(prompt):
            print(f"✅ '{user_input}' confirmed as a fruit.\n")
            return {
                "fruit": user_input,
                "color": state.get("color"),
                "animal": state.get("animal"),
            }
        else:
            print(f"❌ '{user_input}' is not a fruit. Try again.\n")


# -------------------------
# Routing after Fruit
# -------------------------
def route_after_fruit(state: State) -> str:
    fruit = (state.get("fruit") or "").lower()

    if fruit == "orange":
        return "color"
    else:
        # apple and everything else goes to animal
        return "animal"


# -------------------------
# Color Node
# -------------------------
def color_node(state: State) -> State:
    while True:
        user_input = input("🎨 Enter a color: ").strip().lower()

        prompt = f"""
Is "{user_input}" a color?
Answer with ONLY 'YES' or 'NO'.
"""
        if llm_is_valid(prompt):
            print(f"✅ '{user_input}' confirmed as a color.\n")
            return {
                "fruit": state.get("fruit"),
                "color": user_input,
                "animal": state.get("animal"),
            }
        else:
            print(f"❌ '{user_input}' is not a color. Try again.\n")


# -------------------------
# Animal Node
# -------------------------
def animal_node(state: State) -> State:
    while True:
        user_input = input("🐶 Enter an animal: ").strip().lower()

        prompt = f"""
Is "{user_input}" an animal?
Answer with ONLY 'YES' or 'NO'.
"""
        if llm_is_valid(prompt):
            print(f"✅ '{user_input}' confirmed as an animal.\n")
            return {
                "fruit": state.get("fruit"),
                "color": state.get("color"),
                "animal": user_input,
            }
        else:
            print(f"❌ '{user_input}' is not an animal. Try again.\n")


# -------------------------
# Build Graph
# -------------------------
builder = StateGraph(State)

builder.add_node("fruit", fruit_node)
builder.add_node("color", color_node)
builder.add_node("animal", animal_node)

builder.set_entry_point("fruit")

# Conditional routing based on fruit value
builder.add_conditional_edges(
    "fruit",
    route_after_fruit,
    {
        "color": "color",
        "animal": "animal",
    },
)

# After color, always go to animal
builder.add_edge("color", "animal")

builder.add_edge("animal", END)

graph = builder.compile()


# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    final_state = graph.invoke({"fruit": None, "color": None, "animal": None})

    print("🎉 Done!")
    print(f"Fruit:  {final_state['fruit']}")
    print(f"Color:  {final_state['color']}")
    print(f"Animal: {final_state['animal']}")
