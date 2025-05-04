import requests
import json

conversation_state = {
    "name": None,
    "location": None,
    "emergency": None
}

def query_tinyllama(user_message, current_state):
    prompt = f"""
Extract the user's name, location, and emergency from this message.

Respond ONLY with valid JSON like:
{{"name": "...", "location": "...", "emergency": "..."}}

If any value is missing, set it to null.

User message: "{user_message}"
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "tinyllama",
            "prompt": prompt.strip(),
            "stream": False
        }
    )

    raw_output = response.json()["response"].strip()

    try:
        json_start = raw_output.find('{')
        json_end = raw_output.rfind('}') + 1
        json_str = raw_output[json_start:json_end]
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


def next_question():
    if not conversation_state["name"]:
        return "Can I have your name, please?"
    elif not conversation_state["location"]:
        return "What is your location?"
    elif not conversation_state["emergency"]:
        return "What is the emergency?"
    else:
        return "Thank you. Help is on the way."

# Main loop
print("911, how can I help you?")

while not all(conversation_state.values()):
    user_input = input("You: ")
    extracted = query_tinyllama(user_input, conversation_state)

    for key in conversation_state:
        if not conversation_state[key] and extracted[key]:
            conversation_state[key] = extracted[key]

    prompt = next_question()
    print(f"AI: {prompt}")
