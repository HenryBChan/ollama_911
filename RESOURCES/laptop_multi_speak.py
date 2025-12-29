import pyttsx3
import time

def speak(text):
    """Create a fresh engine each time to avoid SAPI5 audio conflicts."""
    engine = pyttsx3.init(driverName="sapi5")
    
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[0].id)
    engine.setProperty("volume", 1.0)
    engine.setProperty("rate", 180)
    
    engine.say(text)
    engine.runAndWait()
    engine.stop()  # release audio device

# Now call speak() multiple times
speak("First sound should play")
time.sleep(1)
speak("Second sound should play")
time.sleep(1)
speak("If you hear this, audio routing is fixed")
