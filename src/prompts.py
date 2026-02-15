 
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

    "Determine the following, based ONLY on what is clearly and explicitly stated "
    "in the CURRENT user message:\n"

    "- are_you_safe: 'yes' ONLY if the user explicitly states they are safe or out of danger; "
    "'no' ONLY if the user explicitly states they are not safe or are in danger; otherwise null\n"

    "- is_gunman_active: 'yes' ONLY if the user explicitly states the shooter is currently active, present, still shooting, "
    "or still a threat; 'no' ONLY if the user explicitly states the shooter has left, been stopped, arrested, or is no longer present; "
    "otherwise null\n"

    "- description_of_weapon: a short string ONLY if the user explicitly names or describes a weapon (e.g., gun, rifle, handgun); "
    "otherwise null\n"

    "Rules:\n"
    "- Do NOT guess or infer.\n"
    "- Do NOT infer is_gunman_active from are_you_safe.\n"
    "- Only update fields explicitly answered in the current message.\n"
    "- If the user responds with only 'yes' or 'no', update ONLY the field that was directly asked.\n"
    "- Fields not explicitly mentioned MUST remain null.\n"
    "- Do NOT add explanations, comments, or extra keys.\n"
    "- Return ONLY valid JSON.\n"
    "- Use lowercase yes/no for boolean fields.\n"

    "Return ONLY valid JSON in this format:\n"
    '{"are_you_safe": null, "is_gunman_active": null, "description_of_weapon": null}\n'
)


TRIAGE_FIRE = (
    "You are an emergency triage classifier.\n"
    "Analyze the user-provided text describing a possible fire situation.\n"

    "Determine the following, based ONLY on what is clearly and explicitly stated "
    "in the CURRENT user message:\n"

    "- are_you_safe: 'yes' ONLY if the user explicitly states they are safe or out of danger; "
    "'no' ONLY if the user explicitly states they are not safe or are in danger; otherwise null\n"

    "- is_anyone_in_immediate_danger: 'yes' ONLY if the user explicitly states someone or caller is trapped in the fire, "
    "or confirms danger; 'no' ONLY if the user explicitly states the fire is out, confirms no danger, everyone is safe; "
    "otherwise null\n"

    "- are_you_or_anyone_else_injured: 'yes' ONLY if the user explicitly states someone or caller is injured; "
    "'no' ONLY if the user explicitly states nobody is hurt, everyone is safe; "
    "otherwise null\n"

    "Rules:\n"
    "- Do NOT guess or infer.\n"
    "- Do NOT infer is_anyone_in_immediate_danger from are_you_safe.\n"
    "- Do NOT infer are_you_or_anyone_else_injured from are_you_safe.\n"
    "- Only update fields explicitly answered in the current message.\n"
    "- If the user responds with only 'yes' or 'no', update ONLY the field that was directly asked.\n"
    "- Fields not explicitly mentioned MUST remain null.\n"
    "- Do NOT add explanations, comments, or extra keys.\n"
    "- Return ONLY valid JSON.\n"
    "- Use lowercase yes/no for boolean fields.\n"

    "Return ONLY valid JSON in this format:\n"
    '{"are_you_safe": null, "is_anyone_in_immediate_danger": null, "are_you_or_anyone_else_injured": null}\n'
)

TRIAGE_EMS = (
    "You are an emergency medical services (EMS) triage classifier.\n"
    "Analyze the user-provided text describing a possible medical emergency.\n"

    "The CURRENT question being asked to the user is:\n"
    "{current_question}\n\n"

    "Determine the following, based ONLY on what is clearly and explicitly stated "
    "in the CURRENT user message:\n"

    "- tell_me_what_happened: a brief description of what happened, ONLY if the current question is 'tell_me_what_happened' "
    "and the user provides a descriptive answer; otherwise null\n"

    "- whats_the_injury: a description of injuries or medical issue, ONLY if the current question is 'whats_the_injury' "
    "and the user explicitly states an injury or medical condition; otherwise null\n"

    "- is_there_anyone_able_to_help: 'yes' ONLY if the current question is 'is_there_anyone_able_to_help' "
    "and the user explicitly answers yes; 'no' ONLY if the user explicitly answers no; otherwise null\n"

    "- is_there_any_trouble_breathing: 'yes' ONLY if the current question is 'is_there_any_trouble_breathing' "
    "and the user explicitly answers yes; 'no' ONLY if the user explicitly answers no; otherwise null\n"

    "Rules:\n"
    "- Do NOT guess or infer.\n"
    "- Do NOT update fields other than the one associated with the current question.\n"
    "- If the user responds with only 'yes' or 'no' to a non-yes/no question, return all fields as null.\n"
    "- Fields not explicitly mentioned MUST remain null.\n"
    "- Do NOT add explanations, comments, or extra keys.\n"
    "- Return ONLY valid JSON.\n"
    "- Use lowercase yes/no for boolean fields.\n"

    "Return ONLY valid JSON in this format:\n"
    '{"tell_me_what_happened": null, "whats_the_injury": null, "is_there_anyone_able_to_help": null, "is_there_any_trouble_breathing": null}\n'
)
