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
