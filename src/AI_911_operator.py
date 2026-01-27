import whisper
import os
import time
from functools import partial
from src.nodes.police_node import police_node
from src.nodes.intake_node import intake_node
from src.nodes.fire_node import fire_node
from src.nodes.EMS_Node import ems_node
from src import prompts as prompts
from src import llm_utils as llm_utils
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

audio_path = "out/recorded_audio.wav"

# TODO
# have location check for street number followed by a string.
# refactor so that the initial triage node then leads into more detailed node

# Load Whisper model (choose"tiny", "base", "small", "medium", or "large")

# -------------------------
# Routing after Intake
# -------------------------
def route_after_intake(state):
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
# State
# -------------------------
out_dir = "out"
wav_path = os.path.join(out_dir, "recorded_audio.wav")
model = whisper.load_model("small")  # Adjust based on speed vs accuracy

class State(TypedDict):
    name: Optional[str]
    location: Optional[str]
    emergency_type: Optional[str]

    # Branch-specific
    fire_details: Optional[str]
    police_details: Optional[str]
    ems_details: Optional[str]
    
intake_with_deps = partial(
    intake_node,
    wav_path=wav_path,
    model=model,
    audio_path=audio_path,
    out_dir=out_dir,
)

police_with_deps = partial(
    police_node,
    out_dir=out_dir,
)
# -------------------------
# Build Graph
# -------------------------
def build_graph():
    builder = StateGraph(State)

    builder.add_node("intake", intake_with_deps)
    builder.add_node("fire", fire_node)
    builder.add_node("police", police_with_deps)
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
    return builder.compile()

def operator_main():

    llm_utils.text_to_speech("9 1 1 what's your emergency?", out_dir)
    
    graph = build_graph()

    final_state = graph.invoke({
        "name": None,
        "location": None,
        "emergency_type": None,
    })

    print("📋 Final Call Summary")
    print(final_state)
    

    # conversation_state = node__initial_triage.conversation_state
    # node__initial_triage.initial_triage_conversation(conversation_state, wav_path, model, audio_path, out_dir)

if __name__ == "__main__":
    operator_main()

