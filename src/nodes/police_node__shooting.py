from src import llm_utils as llm_utils
# -------------------------
# Police Node
# -------------------------
def police_node__shooting(state, out_dir):
    are_you_safe = state.get("police_details__shooting__are_you_safe")
    is_gunman_active = state.get("police_details__shooting__is_gunman_active")
    description_of_weapon = state.get("police_details__shooting__description_of_weapon")
    

    if not are_you_safe or not is_gunman_active or not description_of_weapon:
        # Ask via TTS/GUI instead of input()
        llm_utils.text_to_speech(
            "Please describe what is happening. Theft, assault, suspicious activity, etc.",
            out_dir
        )
        are_you_safe = "foofoo"
        is_gunman_active = "fefefe"
        description_of_weapon = "fufufu" \
        ""
        return {
            **state,
            "police_details__shooting__are_you_safe": are_you_safe,
            "police_details__shooting__is_gunman_active": is_gunman_active,
            "police_details__shooting__description_of_weapon": description_of_weapon,
        }

    # Process details
    print(f"Police details : shooting : are_you_safe : {are_you_safe}")
    print(f"Police details : shooting : is_gunman_active : {is_gunman_active}")
    print(f"Police details : shooting : description_of_weapon : {description_of_weapon}")
    
    return {
        **state,
        "police_details__shooting__are_you_safe": are_you_safe,
        "police_details__shooting__is_gunman_active": is_gunman_active,
        "police_details__shooting__description_of_weapon": description_of_weapon,
    }
