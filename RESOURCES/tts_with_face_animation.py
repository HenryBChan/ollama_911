#pip install pyttsx3

import pyttsx3

def speak(text):
    engine = pyttsx3.init()
    # Try to select a female voice (this varies by OS)
    voices = engine.getProperty('voices')
    for voice in voices:
        if "female" in voice.name.lower() or "Zira" in voice.name or "Samantha" in voice.name:
            engine.setProperty('voice', voice.id)
            break
    engine.say(text)
    engine.runAndWait()

# Example response from your local LLM
response_text = "Hello, have a nice day."
speak(response_text)
