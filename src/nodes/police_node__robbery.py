from src import llm_utils as llm_utils
from src import prompts as prompts 
import time
import os
from pathlib import Path

def next_question(state):
    if state["are_you_safe"] is None:
        return "Are you safe?"
    elif state["is_robbery_ongoing"] is None:
        return "Is the robbery ongoing?"
    elif state["is_anyone_injured"] is None:
        return "Is anyone injured?"
    elif state["description_of_weapon"] is None:
        return "Can you identify the type of weapon?"
    elif state["description_of_suspect"] is None:
        return "Can you give us a description of the suspect?"
    elif state["suspect_whereabouts"] is None:
        return "Can you give a whereabout's of the suspect?"
    else:
        are_you_safe = state["are_you_safe"] 
        is_robbery_ongoing = state["is_robbery_ongoing"] 
        is_anyone_injured = state["is_anyone_injured"]
        description_of_weapon = state["description_of_weapon"]
        description_of_suspect = state["description_of_suspect"]
        suspect_whereabouts = state["suspect_whereabouts"]

        return f"are_you_safe : {are_you_safe}, is_robbery_ongoing {is_robbery_ongoing}, "\
            "is_anyone_injured {is_anyone_injured}, description_of_weapon {description_of_weapon}"\
            "description_of_suspect {description_of_suspect}, suspect_whereabouts {suspect_whereabouts}"
    

# -------------------------
# Police Node
# -------------------------
def police_node__robbery(state, wav_path, model, audio_path, out_dir):
    prev_size = -1

    state_robbery = {
        "are_you_safe": None,
        "is_robbery_ongoing": None,
        "is_anyone_injured": None,
        "description_of_weapon": None,
        "description_of_suspect": None,
        "suspect_whereabouts": None
    }

    prompt = next_question(state_robbery)
    llm_utils.text_to_speech(prompt, out_dir)

    # Wait for a recorded audio file to appear
    while not os.path.exists(wav_path):
        time.sleep(0.5)

    while not all(state_robbery.values()):
        current_size = os.path.getsize(wav_path)
        if current_size != prev_size:
            result = model.transcribe(audio_path)
            text =  result["text"].strip()
            print (f"Trascribed text : {text}")

            # if llm_utils.detect_yes_no(text):
            #     print("Please do not respond with yes/no")
            # else:

            extracted = llm_utils.query_llm(f"{prompt}:{text}", state_robbery, prompts.TRIAGE_ROBBERY)
            
            # try to find key words to figure out the situation
            for key in state_robbery:
                raw_value = extracted.get(key)

                if key in ("are_you_safe", "is_robbery_ongoing", "is_anyone_injured"):
                    new_value = llm_utils.normalize_yes_no(raw_value)
                else:
                    new_value = raw_value

                if key in ("are_you_safe", "is_robbery_ongoing", "is_anyone_injured"):
                    if state_robbery[key] is None and new_value:
                        state_robbery[key] = new_value

                elif key in ("description_of_weapon", "description_of_suspect", "suspect_whereabouts"):
                    if (state_robbery[key] is None and isinstance(new_value, str)) or llm_utils.is_vague_description(state_robbery[key]):
                        if new_value and not llm_utils.is_vague_description(new_value):
                            state_robbery[key] = new_value

            prompt = next_question(state_robbery)
            llm_utils.text_to_speech(prompt, out_dir)

        if all(state_robbery.values()):
            print(f"🚨 Robbery parameters all extracted!")
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
    print(f'Police details : robbery : are_you_safe : {state_robbery["are_you_safe"]}')
    print(f'Police details : robbery : is_robbery_ongoing : {state_robbery["is_robbery_ongoing"]}')
    print(f'Police details : robbery : description_of_weapon : {state_robbery["description_of_weapon"]}')
    print(f'Police details : robbery : is_anyone_injured : {state_robbery["is_anyone_injured"]}')
    print(f'Police details : robbery : description_of_suspect : {state_robbery["description_of_suspect"]}')
    print(f'Police details : robbery : suspect_whereabouts : {state_robbery["suspect_whereabouts"]}')

    return {
        **state,
        "police_details__robbery__are_you_safe": state_robbery["are_you_safe"],
        "police_details__robbery__is_robbery_ongoing": state_robbery["is_robbery_ongoing"],
        "police_details__robbery__description_of_weapon": state_robbery["description_of_weapon"],
        "police_details__robbery__is_anyone_injured": state_robbery["is_anyone_injured"],
        "police_details__robbery__description_of_suspect": state_robbery["description_of_suspect"], 
        "police_details__robbery__suspect_whereabouts": state_robbery["suspect_whereabouts"], 
    }
