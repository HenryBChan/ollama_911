from src import llm_utils as llm_utils
from src import prompts as prompts 
import time
import os
from pathlib import Path

# -------------------------
# Fire Node
# -------------------------
# are_you_safe,
# is_anyone_in_immediate_danger, 
# are_you_or_anyone_else_injured,

def next_question(state):
    if state["are_you_safe"] is None:
        return "Are you safe?"
    elif state["is_anyone_in_immediate_danger"] is None:
        return "Is there anyone in immediate danger?"
    elif state["are_you_or_anyone_else_injured"] is None:
        return "Are you or anyone else injured?"
    else:
        are_you_safe = state["are_you_safe"] 
        is_anyone_in_immediate_danger = state["is_anyone_in_immediate_danger"] 
        are_you_or_anyone_else_injured = state["are_you_or_anyone_else_injured"]

        return f"are_you_safe : {are_you_safe}, is_anyone_in_immediate_danger {is_anyone_in_immediate_danger}, are_you_or_anyone_else_injured {are_you_or_anyone_else_injured}"

# -------------------------
# Fire Node
# -------------------------
def fire_node(state, wav_path, model, audio_path, out_dir):
    prev_size = -1

    state_fire = {
        "are_you_safe": None,
        "is_anyone_in_immediate_danger": None,
        "are_you_or_anyone_else_injured": None
    }

    prompt = next_question(state_fire)
    llm_utils.text_to_speech(prompt, out_dir)

    # Wait for a recorded audio file to appear
    while not os.path.exists(wav_path):
        time.sleep(0.5)

    while not all(state_fire.values()):
        current_size = os.path.getsize(wav_path)
        if current_size != prev_size:
            result = model.transcribe(audio_path)
            text =  result["text"].strip()
            print (f"Trascribed text : {text}")

            # if llm_utils.detect_yes_no(text):
            #     print("Please do not respond with yes/no")
            # else:

            extracted = llm_utils.query_llm(f"{prompt}:{text}", state_fire, prompts.TRIAGE_FIRE)
            
            # try to find key words to figure out the situation
            for key in state_fire:
                raw_value = extracted.get(key)

                if key in ("are_you_safe", "is_anyone_in_immediate_danger", "are_you_or_anyone_else_injured"):
                    new_value = llm_utils.normalize_yes_no(raw_value)
                else:
                    new_value = raw_value

                if key in ("are_you_safe", "is_anyone_in_immediate_danger", "are_you_or_anyone_else_injured"):
                    if state_fire[key] is None and new_value:
                        state_fire[key] = new_value

                # elif key == "description_of_weapon":
                #     if (state_fire[key] is None and isinstance(new_value, str)) or is_vague_gun_description(state_fire[key]):
                #         if new_value and not is_vague_gun_description(new_value):
                #             state_fire[key] = new_value

            prompt = next_question(state_fire)
            llm_utils.text_to_speech(prompt, out_dir)

        if all(state_fire.values()):
            print(f"🚨 Fire parameters all extracted!")
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
    print(f'Fire details : are_you_safe : {state_fire["are_you_safe"]}')
    print(f'Fire details : is_anyone_in_immediate_danger : {state_fire["is_anyone_in_immediate_danger"]}')
    print(f'Fire details : are_you_or_anyone_else_injured : {state_fire["are_you_or_anyone_else_injured"]}')
    
    return {
        **state,
        "fire_details__are_you_safe": state_fire["are_you_safe"],
        "fire_details__is_anyone_in_immediate_danger": state_fire["is_anyone_in_immediate_danger"],
        "fire_details__are_you_or_anyone_else_injured": state_fire["are_you_or_anyone_else_injured"],
    }