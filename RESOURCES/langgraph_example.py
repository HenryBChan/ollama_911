from typing import TypedDict, Optional

from langgraph.graph import StateGraph, END
from langchain_community.llms import Ollama


# -------------------------
# LLM setup (local Ollama)
# -------------------------
llm = Ollama(model="mistral", temperature=0)


# -------------------------
# State definition
# -------------------------
class State(TypedDict):
    fruit: Optional[str]
    animal: Optional[str]


# -------------------------
# Helper: LLM validation
# -------------------------
def llm_is_valid(prompt: str) -> bool:
    """
    Ask the LLM to answer strictly YES or NO.
    """
    response = llm.invoke(prompt).strip().upper()
    return response.startswith("YES")


# -------------------------
# Node 1: Fruit
# -------------------------
def fruit_node(state: State) -> State:
    while True:
        user_input = input("🍎 Enter a fruit: ").strip()

        prompt = f"""
Is "{user_input}" a fruit?
Answer with ONLY 'YES' or 'NO'.
"""
        if llm_is_valid(prompt):
            print(f"✅ '{user_input}' confirmed as a fruit.\n")
            return {"fruit": user_input, "animal": state.get("animal")}
        else:
            print(f"❌ '{user_input}' is not a fruit. Try again.\n")


# -------------------------
# Node 2: Animal
# -------------------------
def animal_node(state: State) -> State:
    while True:
        user_input = input("🐶 Enter an animal: ").strip()

        prompt = f"""
Is "{user_input}" an animal?
Answer with ONLY 'YES' or 'NO'.
"""
        if llm_is_valid(prompt):
            print(f"✅ '{user_input}' confirmed as an animal.\n")
            return {"fruit": state.get("fruit"), "animal": user_input}
        else:
            print(f"❌ '{user_input}' is not an animal. Try again.\n")


# -------------------------
# Build the LangGraph
# -------------------------
builder = StateGraph(State)

builder.add_node("fruit", fruit_node)
builder.add_node("animal", animal_node)

builder.set_entry_point("fruit")
builder.add_edge("fruit", "animal")
builder.add_edge("animal", END)

graph = builder.compile()


# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    final_state = graph.invoke({"fruit": None, "animal": None})

    print("🎉 Done!")
    print(f"Fruit:  {final_state['fruit']}")
    print(f"Animal: {final_state['animal']}")
