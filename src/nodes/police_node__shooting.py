from src import llm_utils as llm_utils
from src import prompts as prompts 
import time
import os
from pathlib import Path

def next_question(state_shooting):
    if not state_shooting["are_you_safe"] and state_shooting["are_you_safe"] != "false":
        return "Are you safe?"
    elif not state_shooting["is_gunman_active"] and state_shooting["is_gunman_active"] != "false":
        return "Is the gunman stil active?"
    elif not state_shooting["description_of_weapon"]:
        return "Can you identify the type of weapon?"
    else:
        are_you_safe = state_shooting["are_you_safe"] 
        is_gunman_active = state_shooting["is_gunman_active"] 
        description_of_weapon = state_shooting["description_of_weapon"]

        return f"are_you_safe : {are_you_safe}, is_gunman_active {is_gunman_active}, description_of_weapon {description_of_weapon}"
    
# -------------------------
# Police Node
# -------------------------
def police_node__shooting(state, wav_path, model, audio_path, out_dir):
    # are_you_safe = state.get("police_details__shooting__are_you_safe")
    # is_gunman_active = state.get("police_details__shooting__is_gunman_active")
    # description_of_weapon = state.get("police_details__shooting__description_of_weapon")
    

    # if not are_you_safe or not is_gunman_active or not description_of_weapon:
        # # Ask via TTS/GUI instead of input()
        # llm_utils.text_to_speech(
        #     "Please describe what is happening. Theft, assault, suspicious activity, etc.",
        #     out_dir
        # )
        # are_you_safe = "foofoo"
        # is_gunman_active = "fefefe"
        # description_of_weapon = "fufufu" \
        # ""
        # return {
        #     **state,
        #     "police_details__shooting__are_you_safe": are_you_safe,
        #     "police_details__shooting__is_gunman_active": is_gunman_active,
        #     "police_details__shooting__description_of_weapon": description_of_weapon,
        # }


    prev_size = -1

    state_shooting = {
        "are_you_safe": None,
        "is_gunman_active": None,
        "description_of_weapon": None
    }

    # Wait for a recorded audio file to appear
    while not os.path.exists(wav_path):
        time.sleep(0.5)

    while not all(state_shooting.values()):
        current_size = os.path.getsize(wav_path)
        if current_size != prev_size:
            result = model.transcribe(audio_path)
            text =  result["text"].strip()
            print (f"Trascribed text : {text}")

            if llm_utils.detect_yes_no(text):
                print("Please do not respond with yes/no")
            else:
                extracted = llm_utils.query_llm(text, state_shooting, prompts.TRIAGE_POLICE_SHOOTING)

                # try to find key words to figure out the situation
                for key in state_shooting:
                    new_value = extracted.get(key)
    
                    if key == "are_you_safe":
                        if (not state_shooting[key]):
                            if new_value:
                                state_shooting[key] = new_value

                    elif key == "is_gunman_active":
                        if (not state_shooting[key]):
                            if new_value:
                                state_shooting[key] = new_value

                    elif not state_shooting[key] and new_value:
                        state_shooting[key] = new_value

            prompt = next_question(state_shooting)
            llm_utils.text_to_speech(prompt, out_dir)

        if all(state_shooting.values()):
            print(f"🚨 Shooting parameters all extracted!")
            # services = dispatch_services(state_shooting)
            # print(f"🚨 Dispatching: {', '.join(services)}")

            # Define the file path
            path = Path("out") / "close.gui"
            # Make sure the directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            # Create the blank file (or update its timestamp if it already exists)
            path.touch(exist_ok=True)
            break

        prev_size = current_size
        time.sleep(0.5)

    # Process details
    print(f'Police details : shooting : are_you_safe : {state_shooting["are_you_safe"]}')
    print(f'Police details : shooting : is_gunman_active : {state_shooting["is_gunman_active"]}')
    print(f'Police details : shooting : description_of_weapon : {state_shooting["description_of_weapon"]}')
    
    return {
        **state,
        "police_details__shooting__are_you_safe": state_shooting["are_you_safe"],
        "police_details__shooting__is_gunman_active": state_shooting["is_gunman_active"],
        "police_details__shooting__description_of_weapon": state_shooting["description_of_weapon"],
    }
