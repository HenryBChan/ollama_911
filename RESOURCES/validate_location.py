import requests
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"

def ollama_prompt(system_prompt, user_prompt):
    payload = {
        "model": MODEL,
        "prompt": f"{system_prompt}\n\nUser: {user_prompt}\nAssistant:",
        "stream": False
    }
    r = requests.post(OLLAMA_URL, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()["response"].strip()


# ----------------------------
# Address Validation
# ----------------------------

def validate_address(address: str):
    """
    Very simple validation:
    - Street number
    - Street name
    - City
    - Province/state
    - Postal/ZIP code
    """
    missing = []

    if not re.search(r"\d+", address):
        missing.append("street number")

    if not re.search(r"\b(st|street|ave|avenue|rd|road|blvd|lane|ln|dr|drive)\b", address.lower()):
        missing.append("street name")

    if not re.search(r",", address):
        missing.append("city (separate parts with commas)")

    if not re.search(r"\b(ON|QC|BC|AB|MB|SK|NS|NB|NL|PE|YT|NT|NU|CA|NY|TX|WA)\b", address):
        missing.append("province/state")

    if not re.search(r"\b[A-Z]\d[A-Z]\s?\d[A-Z]\d|\b\d{5}\b", address):
        missing.append("postal/ZIP code")

    return missing


# ----------------------------
# Conversation Flow
# ----------------------------

SYSTEM_PROMPT = (
    "You are a friendly pizza ordering assistant. "
    "You ask one question at a time. "
    "You do not move on until the current question is answered correctly."
)

def main():
    print("🍕 Welcome to AI Pizza Ordering 🍕\n")

    # ---- LOCATION STEP ----
    while True:
        user_location = input("📍 What is your full delivery address?\n> ")

        missing = validate_address(user_location)

        if missing:
            explanation = (
                "Your address is missing the following required parts: "
                + ", ".join(missing)
                + ".\nPlease provide a complete address "
                  "(street number, street name, city, province/state, postal/ZIP code)."
            )

            ai_response = ollama_prompt(SYSTEM_PROMPT, explanation)
            print(f"\n🤖 {ai_response}\n")
        else:
            print("\n✅ Address confirmed!\n")
            break

    # ---- PIZZA QUESTIONS ----
    questions = [
        "What size pizza would you like? (small, medium, large)",
        "What type of crust would you like? (thin, regular, deep dish)",
        "What toppings would you like?",
        "Would you like anything to drink?",
        "Is this order for delivery or pickup?"
    ]

    order = {}

    for q in questions:
        ai_question = ollama_prompt(SYSTEM_PROMPT, q)
        print(f"🤖 {ai_question}")
        answer = input("> ")
        order[q] = answer
        print()

    # ---- SUMMARY ----
    summary_prompt = (
        "Summarize the following pizza order in a friendly confirmation message:\n"
        f"Address: {user_location}\n"
    )
    for k, v in order.items():
        summary_prompt += f"{k}: {v}\n"

    summary = ollama_prompt(SYSTEM_PROMPT, summary_prompt)

    print("🧾 Order Summary")
    print("-----------------")
    print(summary)
    print("\n🍕 Thank you for your order!")


if __name__ == "__main__":
    main()
