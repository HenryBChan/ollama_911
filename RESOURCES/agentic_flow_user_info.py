import requests

# Simple state tracker
conversation_state = {
    "name": None,
    "location": None,
    "emergency": None
}

def generate_prompt(conversation, model="tinyllama"):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": conversation,
            "stream": False
        }
    )
    return response.json()["response"]

def extract_info(response):
    # Very basic rules-based extraction for now
    info = {
        "name": None,
        "location": None,
        "emergency": None
    }
    response_lower = response.lower()

    if any(word in response_lower for word in ["my name is", "i am", "this is"]) and conversation_state["name"] is None:
        tokens = response.split()
        try:
            name_index = tokens.index("name") + 2  # assumes "my name is"
            info["name"] = tokens[name_index]
        except:
            pass

    if any(loc in response_lower for loc in ["i'm at", "i am at", "location is", "address is"]) and conversation_state["location"] is None:
        info["location"] = response

    if any(word in response_lower for word in ["help", "emergency", "fire", "hurt", "accident"]) and conversation_state["emergency"] is None:
        info["emergency"] = response

    return info

def next_question():
    if not conversation_state["name"]:
        return "Can I have your name, please?"
    elif not conversation_state["location"]:
        return "What is your location?"
    elif not conversation_state["emergency"]:
        return "What is the emergency?"
    else:
        return "Thank you. Help is on the way."

# Conversation loop
print("911, how can I help you?")

while not all(conversation_state.values()):
    user_input = input("You: ")
    info = extract_info(user_input)
    
    for key in conversation_state:
        if not conversation_state[key] and info[key]:
            conversation_state[key] = info[key]
    
    prompt = next_question()
    print(f"AI: {prompt}")
