# -------------------------
# Fire Node
# -------------------------
def fire_node(state):
    print("🔥 FIRE DISPATCH\n")
    print(f"Caller:   {state['name']}")
    print(f"Location: {state['location']}\n")

    details = input("What is on fire? (house, car, bush, etc): ").strip()

    print("\n🚒 Fire details recorded.")
    print(f"Fire type: {details}\n")

    return state