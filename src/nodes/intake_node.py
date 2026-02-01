import re
import os
from src import llm_utils as llm_utils
from src import prompts as prompts 
import time




def is_vague_emergency(description):
    if not description:
        return True
    vague_terms = ["Not Provided", "None", "help", "emergency", "problem", "issue", "situation"]
    return description.strip().lower() in vague_terms

#Apartment / unit number
#Cross streets
#City / town
#“Are you inside or outside?”
#“Is that correct?” (confirmation)
def is_vague_location(loc):
    if not loc:
        return True
    vague_terms = [
        "Not Provided", "None",
        "somewhere", "around", "maybe", "not sure", "i don't know", 
        "don't know", "unknown", "lost", "nearby", "far away", "an island"
    ]
    return any(term in loc.lower() for term in vague_terms)

def format_emergency(emergency):
    if not emergency or emergency.lower() in ["yes", "no", "true", "false", "help", "emergency"]:
        return "unspecified emergency"

    # Basic cleanup
    emergency_clean = re.sub(r"\b(my|i have|i’m|i am|the)\b", "", emergency, flags=re.IGNORECASE).strip()
    emergency_clean = emergency_clean[0].lower() + emergency_clean[1:]

    if "fire" in emergency_clean:
        if "house" in emergency_clean:
            return "house fire emergency"
        return f"{emergency_clean} emergency"
    elif any(word in emergency_clean for word in ["broken", "neck", "injury", "hurt", "bleeding", "cut", "pain"]):
        return f"{emergency_clean} emergency"
    else:
        return f"{emergency_clean} emergency"

def next_question(conversation_state):
    if not conversation_state["name"]:
        return "Can I have your name, please?"
    elif not conversation_state["location"]:
        return "What is the address of your emergency?"
    elif not conversation_state["emergency"]:
        return "What is the emergency?"
    else:
        name = conversation_state["name"] or "unknown"
        location = conversation_state["location"] or "unspecified location"
        emergency = format_emergency(conversation_state["emergency"])

        return f"{name}, we received your {emergency} at {location}. Help is on the way."
    
def intake_node(state, wav_path, model, audio_path, out_dir):
    prev_size = -1

    conversation_state = {
        "name": None,
        "location": None,
        "emergency": None
    }

    # Wait for a recorded audio file to appear
    while not os.path.exists(wav_path):
        time.sleep(0.5)

    while not all(conversation_state.values()):
        current_size = os.path.getsize(wav_path)
        if current_size != prev_size:
            result = model.transcribe(audio_path)
            text =  result["text"].strip()
            print (f"Trascribed text : {text}")

            extracted = llm_utils.query_llm(text, conversation_state, prompts.INITIAL_TRIAGE)
           
           # try to find key words to figure out the situation
            for key in conversation_state:
                new_value = extracted.get(key)
 
                if key == "emergency":
                    if (not conversation_state[key]) or is_vague_emergency(conversation_state[key]):
                        if new_value and not is_vague_emergency(new_value):
                            conversation_state[key] = new_value

                elif key == "location":
                    if (not conversation_state[key]) or is_vague_location(conversation_state[key]):
                        if new_value and not is_vague_location(new_value):
                            conversation_state[key] = new_value

                elif not conversation_state[key] and new_value:
                    conversation_state[key] = new_value

            # Re-check location vagueness
            if conversation_state["location"] and is_vague_location(conversation_state["location"]):
                outgoing_message = "Can you be more specific about your location? Any nearby landmarks or street names?"
                llm_utils.text_to_speech(outgoing_message, out_dir)
                continue

            if conversation_state["emergency"] and is_vague_emergency(conversation_state["emergency"]):
                # print (f'DEBUG {conversation_state["emergency"]}')
                outgoing_message = "Can you briefly describe what the emergency is?"
                llm_utils.text_to_speech(outgoing_message, out_dir)
                continue
            
            prompt = next_question(conversation_state)
            llm_utils.text_to_speech(prompt, out_dir)

        if all(conversation_state.values()):
            services = dispatch_services(conversation_state)
            print(f"🚨 Dispatching: {', '.join(services)}")

            os.remove(wav_path)

            # # Define the file path
            # path = Path("out") / "close.gui"
            # # Make sure the directory exists
            # path.parent.mkdir(parents=True, exist_ok=True)
            # # Create the blank file (or update its timestamp if it already exists)
            # path.touch(exist_ok=True)
            break

        prev_size = current_size
        time.sleep(0.5)

    return {
        "name": conversation_state["name"],
        "location": conversation_state["location"],
        "emergency_type": conversation_state["emergency"],
    }

def dispatch_services(state):
    """
    Determine which emergency services to dispatch based on the emergency description.
    Returns a list of services like: ['EMS', 'Fire Department']
    """
    services = set()
    emergency = (state.get("emergency") or "").lower()

    # Dispatch logic based on keywords
    if any(term in emergency for term in ["broken", "bleeding", "hurt", "injury", "unconscious", "pain", "neck", "heart attack", "stroke"]):
        services.add("EMS")

    if any(term in emergency for term in ["fire", "smoke", "burning", "explosion"]):
        services.add("Fire Department")

    if any(term in emergency for term in ["shooting"]):
        services.add("Police__shooting")
        
    if any(term in emergency for term in ["robbery", "assault", "theft", "violence", "gun", "knife", "threat"]):
        services.add("Police")

    if any(term in emergency for term in ["chemical", "hazmat", "toxic", "radiation", "spill", "gas leak"]):
        services.add("HazMat Team")

    if not services:
        services.add("General Emergency Dispatcher")  # Catch-all fallback

    return list(services)
