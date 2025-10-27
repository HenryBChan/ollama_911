import whisper
import os
import time
# import ollama
import pyttsx3
import re
import requests
import json
from pathlib import Path

audio_path = "out/recorded_audio.wav"

conversation_state = {
    "name": None,
    "location": None,
    "emergency": None
}

# Load Whisper model (choose"tiny", "base", "small", "medium", or "large")
model = whisper.load_model("small")  # Adjust based on speed vs accuracy

# convert audio file to text using whisper
def transcribe_audio(audio_path):
    print("Transcribing audio...")
    result = model.transcribe(audio_path)
    return result["text"].strip()

def microphone_transcribe():
    # print("Voice Assistant Started! Say something...\n")

    transcribed_text = transcribe_audio(audio_path)
    print (f"Trascribed text : {transcribed_text}")
     
    # if transcribed_text.lower() == "exit.":
    #     print("Exiting microphone listener...")
    #     break    

    # if transcribed_text and is_valid_text(transcribed_text):  # Only write if text is not empty
    #     f.write(f"send:{transcribed_text}\n")
    #     f.flush()
    # time.sleep(0.5)
    return transcribed_text

# Process text with TinyLlama (Ollama)
# def process_text_with_tinyllama(text):
#     print("Processing with TinyLlama...")
#     response = ollama.chat(model="tinyllama", messages=[{"role": "user", "content": text}])
#     return response["message"]["content"]
def query_tinyllama(user_message, current_state):
    prompt = f"""
Extract the user's name, location, and emergency description from the message.

- Emergency should be a short description of what help is needed (e.g., "broken leg", "house fire", "car accident").
- Only return valid JSON in the following format:
  {{"name": ..., "location": ..., "emergency": ...}}
- Only include values that were clearly and explicitly stated by the user.
- If any value is NOT directly stated, set it to null.
- Do NOT guess or default to placeholders like "User", "Not Provided", "None", "Anonymous", or "Unknown".
- Do NOT explain or output code. Only return a JSON object.
- DO NOT guess or infer names like "user", "drowning user", or similar.

User message: "{user_message}"
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt.strip(),
            "stream": False
        }
    )

    raw_output = response.json()["response"].strip()
    print("🧠 LLM raw output:", raw_output)  # helpful debug{}

    try:
        match = re.search(r'\{.*?\}', raw_output, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in LLM response")
        json_str = match.group(0)
        parsed = json.loads(json_str)
        return {
            "name": parsed.get("name", current_state["name"]),
            "location": parsed.get("location", current_state["location"]),
            "emergency": parsed.get("emergency", current_state["emergency"])
        }
    except Exception as e:
        print("⚠️ Could not parse LLM response:", raw_output)
        # Return the current state unchanged
        return current_state.copy()


# Text-to-speech
def text_to_speech(text, out_dir):
    print(f"TinyLlama Response: {text}")
    # tts_engine.say(text)
    # tts_engine.runAndWait()
    with open(f"{out_dir}/operator_voice.txt", "w", encoding="utf-8") as f:
        f.write(text)

def is_vague_emergency(description):
    if not description:
        return True
    vague_terms = ["Not Provided", "None", "help", "emergency", "problem", "issue", "situation"]
    return description.strip().lower() in vague_terms

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
        return "What is your location?"
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

    # # Initialize text to speech engine
    # tts_engine = pyttsx3.init()

    # time.sleep(1.5)
    text_to_speech("9 1 1 what's your emergency?", out_dir)
    
    print(f"Waiting for {wav_path} to be created...")

    # Wait for the file to appear
    while not os.path.exists(wav_path):
        time.sleep(0.5)
    
    prev_size = -1

    while not all(conversation_state.values()):
        current_size = os.path.getsize(wav_path)
        if current_size != prev_size:
            text = microphone_transcribe()
            extracted = query_tinyllama(text, conversation_state)
           
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
            
            # try to extract important information (emergency_type(fire, ...), location, ) 
            # review what information is missing
            # if information is missing then 
            #    create a message - ask user to clarify and repeat from beginning
            # else
            #    review emergecy and if it is an emergency
            #    if emergency
            #       if we need to escalate to human
            #           message - "connecting with my human supervisor"
            #       else
            #           initiate emergency servcies to dispatch
            #           message - "emergency services are dispatched"
            #    else
            #       message - "sorry your <emergency_type> is not considered an emergency, would you like to restate"
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

