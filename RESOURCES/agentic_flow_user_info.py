import requests
import json
import re

conversation_state = {
    "name": None,
    "location": None,
    "emergency": None
}

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



def format_emergency(emergency):
    if not emergency or emergency.lower() in ["yes", "no", "true", "false"]:
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

def is_vague_location(loc):
    if not loc:
        return True
    vague_terms = [
        "somewhere", "around", "maybe", "not sure", "i don't know", 
        "don't know", "unknown", "lost", "nearby", "far away", "an island"
    ]
    return any(term in loc.lower() for term in vague_terms)


# Main loop
print("911, how can I help you?")

while not all(conversation_state.values()):
    user_input = input("You: ")
    extracted = query_tinyllama(user_input, conversation_state)

    for key in conversation_state:
        if not conversation_state[key] and extracted[key]:
            conversation_state[key] = extracted[key]

    # Re-check location vagueness
    if conversation_state["location"] and is_vague_location(conversation_state["location"]):
        print("AI: Can you be more specific about your location? Any nearby landmarks or street names?")
        continue
    
    prompt = next_question()
    print(f"AI: {prompt}")

#Simulate which responders are sent based on emergency type.
#Store the record (e.g., to a file or mock database).
#dispatch_services(conversation_state)
if all(conversation_state.values()):
    services = dispatch_services(conversation_state)
    print(f"🚨 Dispatching: {', '.join(services)}")

