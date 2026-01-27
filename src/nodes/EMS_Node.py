# -------------------------
# EMS Node
# -------------------------
def ems_node(state):
    print("🚑 EMS DISPATCH\n")
    print(f"Caller:   {state['name']}")
    print(f"Location: {state['location']}\n")

    details = input("What is the medical emergency? ").strip()

    print("\n🩺 EMS details recorded.")
    print(f"Medical issue: {details}\n")

    return state