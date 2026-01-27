from src import llm_utils as llm_utils
# -------------------------
# Police Node
# -------------------------
def police_node(state, out_dir):
    details = state.get("police_details")

    if not details:
        # Ask via TTS/GUI instead of input()
        llm_utils.text_to_speech(
            "Please describe what is happening. Theft, assault, suspicious activity, etc.",
            out_dir
        )
        return state

    # Process details
    print(f"Police details: {details}")

    return {
        **state,
        "police_details": details,
    }
