 
INITIAL_TRIAGE = ( 
    "Extract name, location, and emergency.\n"
    "Emergency should be a short description of what help is needed (e.g., 'broken leg', 'house fire', 'car accident'.\n"
    "Only include values that were clearly and explicitly stated by the user.\n"
    "Return ONLY valid JSON:\n"
    "DO NOT guess or infer names like 'user', 'drowning user', or similar.\n"
    '{"name": null, "location": null, "emergency": null}\n' 
)


