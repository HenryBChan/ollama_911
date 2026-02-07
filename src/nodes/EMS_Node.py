import os
import time
from src import llm_utils
from src import prompts
from pathlib import Path

def next_question(state):
    if state["tell_me_what_happened"] is None:
        return "Tell me what happened?"
    elif state["how_are_you_injured"] is None:
        return "How are you injured?"
    elif state["is_there_anyone_able_to_help"] is None:
        return "Is ther anyone around who might be able to help?"
    elif state["is_the_patient_awake_and_responding"] is None:
        return "Is the patient awake and responding?"
    else:
        tell_me_what_happened = state["tell_me_what_happened"] 
        how_are_you_injured = state["how_are_you_injured"] 
        is_there_anyone_able_to_help = state["is_there_anyone_able_to_help"]
        is_the_patient_awake_and_responding = state["is_the_patient_awake_and_responding"]
        return f"tell_me_what_happened : {tell_me_what_happened}, how_are_you_injured {how_are_you_injured}, "\
            "is_there_anyone_able_to_help {is_there_anyone_able_to_help}, "\
            "is_the_patient_awake_and_responding {is_the_patient_awake_and_responding}"



# -------------------------
# EMS Node
# -------------------------
def ems_node(state, wav_path, model, audio_path, out_dir):
    prev_size = -1

    state_ems = {
        "tell_me_what_happened": None,
        "how_are_you_injured": None,
        "is_there_anyone_able_to_help": None,
        "is_the_patient_awake_and_responding": None
    }

    prompt = next_question(state_ems)
    llm_utils.text_to_speech(prompt, out_dir)

    # Wait for a recorded audio file to appear
    while not os.path.exists(wav_path):
        time.sleep(0.5)

    while not all(state_ems.values()):
        current_size = os.path.getsize(wav_path)
        if current_size != prev_size:
            result = model.transcribe(audio_path)
            text =  result["text"].strip()
            print (f"Trascribed text : {text}")

            extracted = llm_utils.query_llm(f"{prompt}:{text}", state_ems, prompts.TRIAGE_EMS)
            
            # try to find key words to figure out the situation
            for key in state_ems:
                raw_value = extracted.get(key)

                if key in ("how_are_you_injured", "is_there_anyone_able_to_help", "is_the_patient_awake_and_responding"):
                    new_value = llm_utils.normalize_yes_no(raw_value)
                else:
                    new_value = raw_value

                if key in ("how_are_you_injured", "is_there_anyone_able_to_help", "is_the_patient_awake_and_responding"):
                    if state_ems[key] is None and new_value:
                        state_ems[key] = new_value

                elif key == "tell_me_what_happened":
                    if (state_ems[key] is None and isinstance(new_value, str)) or llm_utils.is_vague_description(state_ems[key]):
                        if new_value and not llm_utils.is_vague_description(new_value):
                            state_ems[key] = new_value

            prompt = next_question(state_ems)
            llm_utils.text_to_speech(prompt, out_dir)

        if all(state_ems.values()):
            print(f"🚨 EMS parameters all extracted!")
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
    print(f'Ems details : tell_me_what_happened : {state_ems["tell_me_what_happened"]}')
    print(f'Ems details : how_are_you_injured : {state_ems["how_are_you_injured"]}')
    print(f'Ems details : is_there_anyone_able_to_help : {state_ems["is_there_anyone_able_to_help"]}')
    print(f'Ems details : is_the_patient_awake_and_responding : {state_ems["is_the_patient_awake_and_responding"]}')
    
    return {
        **state,
        "Ems_details__tell_me_what_happened": state_ems["tell_me_what_happened"],
        "Ems_details__how_are_you_injured": state_ems["how_are_you_injured"],
        "Ems_details__is_there_anyone_able_to_help": state_ems["is_there_anyone_able_to_help"],
        "Ems_details__is_the_patient_awake_and_responding": state_ems["is_the_patient_awake_and_responding"],
    }