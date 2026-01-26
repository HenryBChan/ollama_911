import whisper
import os
import time
from functools import partial
# from src import node__initial_triage as intake_node
from src.intake_node import intake_node

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
# State
# -------------------------
class State(TypedDict):
    name: Optional[str]
    location: Optional[str]
    emergency_type: Optional[str]
    
model = whisper.load_model("small")  # Adjust based on speed vs accuracy

# -------------------------
# Helper
# -------------------------
# def llm_is_valid(prompt: str) -> bool:
#     response = llm.invoke(prompt).strip().upper()
#     return response.startswith("YES")



out_dir = "out"
wav_path = os.path.join(out_dir, "recorded_audio.wav")

intake_with_deps = partial(
    intake_node,
    wav_path=wav_path,
    model=model,
    audio_path=audio_path,
    out_dir=out_dir,
)

# -------------------------
# Build Graph
# -------------------------
def build_graph():
    builder = StateGraph(State)

    builder.add_node("intake", intake_with_deps)

    builder.set_entry_point("intake")

    builder.add_edge("intake", END)

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

