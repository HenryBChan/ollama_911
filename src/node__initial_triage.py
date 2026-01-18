import re

conversation_state = {
    "name": None,
    "location": None,
    "emergency": None
}

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
    
