 
INITIAL_TRIAGE = ( 
    "Extract name, location, and emergency.\n"
    "Emergency should be a short description of what help is needed (e.g., 'broken leg', 'house fire', 'car accident'.\n"
    "Only include values that were clearly and explicitly stated by the user.\n"
    "Return ONLY valid JSON:\n"
    "DO NOT guess or infer names like 'user', 'drowning user', or similar.\n"
    '{"name": null, "location": null, "emergency": null}\n' 
)

TRIAGE_POLICE_SHOOTING = (
    "You are an emergency triage classifier.\n"

    "Analyze the user-provided text describing a possible shooting situation.\n"

    "Determine the following, based ONLY on what is clearly and explicitly stated:\n"
    "- are_you_safe: true if the user explicitly states they are safe or out of danger; otherwise false\n"
    "- is_gunman_active: true if the shooter is described as yes, maybe, currently active, present, or still a threat; otherwise false\n"
    "- description_of_weapon: true if any firearm or weapon is explicitly described (e.g., gun, rifle, handgun); otherwise false\n"

    "Rules:\n"
    "- Do NOT guess or infer.\n"
    "- If the text is unclear or does not explicitly state something, return null.\n"
    "- Do NOT add explanations, comments, or extra keys.\n"
    "- Return ONLY valid JSON.\n"
    "- Use lowercase true/false for the 'are_you_safe' and 'is_gunman_active' (JSON booleans).\n"
    "- For 'description_of_weapon' return a short string description of weapon"

    "Return ONLY valid JSON:\n"
    "DO NOT guess or infer names like 'user', 'drowning user', or similar.\n"
    '{"are_you_safe": null, "is_gunman_active": null, "description_of_weapon": null}\n' 

)