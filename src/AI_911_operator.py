import whisper
import os
import time
import re
import json
import gc
import subprocess

from pathlib import Path

audio_path = "out/recorded_audio.wav"

conversation_state = {
    "name": None,
    "location": None,
    "emergency": None
}

# Load Whisper model (choose"tiny", "base", "small", "medium", or "large")
model = whisper.load_model("small")  # Adjust based on speed vs accuracy


def clean_llm_output(text: str) -> str:
    ANSI_ESCAPE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
    # Remove ANSI escape codes
    text = ANSI_ESCAPE.sub("", text)

    # Remove markdown code fences
    text = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE)

    return text.strip()

def query_llm(user_message, current_state):
    # HARD truncate user input (critical)
    user_message = user_message[:500]

    # Keep prompt extremely small
    prompt = (
        "Extract name, location, and emergency.\n"

        "Emergency should be a short description of what help is needed (e.g., 'broken leg', 'house fire', 'car accident'.\n"
        "Only include values that were clearly and explicitly stated by the user.\n"
        "Return ONLY valid JSON:\n"
        "DO NOT guess or infer names like 'user', 'drowning user', or similar.\n"
        '{"name": null, "location": null, "emergency": null}\n'
        f'Text: "{user_message}"\n'
        "JSON:"
    )

    try:
        result = subprocess.run(
            ["ollama", "run", "gemma2:2b", prompt],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=120
        )

        # "model": "mistral",       # requires 4.5 Gb mem
        # "model": "phi3:3.8b",
        # "model": "tinyllama:1.1b",
        # "model": "phi3:mini",       # requires more mem
        # "model": "gemma2:2b",

        raw_output = clean_llm_output(result.stdout)
        print(f"raw_output {raw_output}")
    except subprocess.TimeoutExpired:
        print("⏱ Ollama subprocess timed out")
        return current_state.copy()

    except Exception as e:
        print("❌ Ollama request failed:", e)
        return current_state.copy()

    # Immediately drop references we no longer need
    del result
    # del data
    gc.collect()

    # Parse JSON safely
    try:
        match = re.search(r"\{.*\}", raw_output, re.DOTALL)
        if not match:
            return current_state.copy()

        parsed = json.loads(match.group(0))

        return {
            "name": parsed.get("name", current_state["name"]),
            "location": parsed.get("location", current_state["location"]),
            "emergency": parsed.get("emergency", current_state["emergency"])
        }

    except Exception:
        return current_state.copy()

# Text-to-speech
def text_to_speech(text, out_dir):
    print(f"Operator Response: {text}")
    with open(f"{out_dir}/operator_voice.txt", "w", encoding="utf-8") as f:
        f.write(text)

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
    
def next_question():
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

    if any(term in emergency for term in ["shooting", "robbery", "assault", "theft", "violence", "gun", "knife", "threat"]):
        services.add("Police")

    if any(term in emergency for term in ["chemical", "hazmat", "toxic", "radiation", "spill", "gas leak"]):
        services.add("HazMat Team")

    if not services:
        services.add("General Emergency Dispatcher")  # Catch-all fallback

    return list(services)

out_dir = "out"
wav_path = os.path.join(out_dir, "recorded_audio.wav")

def operator_main():

    text_to_speech("9 1 1 what's your emergency?", out_dir)
    
    # Wait for a recorded audio file to appear
    while not os.path.exists(wav_path):
        time.sleep(0.5)
    
    prev_size = -1

    while not all(conversation_state.values()):
        current_size = os.path.getsize(wav_path)
        if current_size != prev_size:
            result = model.transcribe(audio_path)
            text =  result["text"].strip()
            print (f"Trascribed text : {text}")

            extracted = query_llm(text, conversation_state)
           
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
                text_to_speech(outgoing_message, out_dir)
                continue

            if conversation_state["emergency"] and is_vague_emergency(conversation_state["emergency"]):
                # print (f'DEBUG {conversation_state["emergency"]}')
                outgoing_message = "Can you briefly describe what the emergency is?"
                text_to_speech(outgoing_message, out_dir)
                continue
            
            prompt = next_question()
            text_to_speech(prompt, out_dir)

        if all(conversation_state.values()):
            services = dispatch_services(conversation_state)
            print(f"🚨 Dispatching: {', '.join(services)}")

            # Define the file path
            path = Path("out") / "close.gui"
            # Make sure the directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            # Create the blank file (or update its timestamp if it already exists)
            path.touch(exist_ok=True)
            break

        prev_size = current_size
        time.sleep(0.5)

if __name__ == "__main__":
    operator_main()

