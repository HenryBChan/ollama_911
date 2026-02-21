from src import llm_utils as llm_utils
from src import prompts as prompts 
import time
import os
from pathlib import Path

# -------------------------
# Car accident Node
# -------------------------
# is_anyone_injured
# tell_me_what_happened
# have_you_exchanged_information
def next_question(state):
    if state["is_anyone_injured"] is None:
        return "Is anyone injured?"
    elif state["tell_me_what_happened"] is None:
        return "Tell me what happened?"
    elif state["have_you_exchanged_information"] is None:
        return "Have you exchanged information?"
    else:
        is_anyone_injured = state["is_anyone_injured"] 
        tell_me_what_happened = state["tell_me_what_happened"] 
        have_you_exchanged_information = state["have_you_exchanged_information"]

        return f"is_anyone_injured : {is_anyone_injured}, tell_me_what_happened {tell_me_what_happened}, have_you_exchanged_information {have_you_exchanged_information}"

# -------------------------
# Fire Node
# -------------------------
def police_node__car_accident(state, wav_path, model, audio_path, out_dir):
    prev_size = -1

    state_car_accident = {
        "is_anyone_injured": None,
        "tell_me_what_happened": None,
        "have_you_exchanged_information": None
    }

    prompt = next_question(state_car_accident)
    llm_utils.text_to_speech(prompt, out_dir)

    # Wait for a recorded audio file to appear
    while not os.path.exists(wav_path):
        time.sleep(0.5)

    while not all(state_car_accident.values()):
        current_size = os.path.getsize(wav_path)
        if current_size != prev_size:
            result = model.transcribe(audio_path)
            text =  result["text"].strip()
            print (f"Trascribed text : {text}")

            extracted = llm_utils.query_llm(f"{prompt}:{text}", state_car_accident, prompts.TRIAGE_CAR_ACCIDENT)
            
            # try to find key words to figure out the situation
            for key in state_car_accident:
                raw_value = extracted.get(key)

                if key in ("is_anyone_injured", "have_you_exchanged_information"):
                    new_value = llm_utils.normalize_yes_no(raw_value)
                else:
                    new_value = raw_value

                if key in ("is_anyone_injured", "have_you_exchanged_information"):
                    if state_car_accident[key] is None and new_value:
                        state_car_accident[key] = new_value

                elif key == "tell_me_what_happened":
                    if (state_car_accident[key] is None and isinstance(new_value, str)) or llm_utils.is_vague_description(state_car_accident[key]):
                        if new_value and not llm_utils.is_vague_description(new_value):
                            state_car_accident[key] = new_value

            prompt = next_question(state_car_accident)
            llm_utils.text_to_speech(prompt, out_dir)

        if all(state_car_accident.values()):
            print(f"🚨 Car accident parameters all extracted!")
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
    print(f'Police details : is_anyone_injured : {state_car_accident["is_anyone_injured"]}')
    print(f'Police details : tell_me_what_happened : {state_car_accident["tell_me_what_happened"]}')
    print(f'Police details : have_you_exchanged_information : {state_car_accident["have_you_exchanged_information"]}')
    
    return {
        **state,
        "police_details__car_accident__is_anyone_injured": state_car_accident["is_anyone_injured"],
        "police_details__car_accident__tell_me_what_happened": state_car_accident["tell_me_what_happened"],
        "police_details__car_accident__have_you_exchanged_information": state_car_accident["have_you_exchanged_information"],
    }
# is_anyone_injured
# tell_me_what_happened
# have_you_exchanged_information