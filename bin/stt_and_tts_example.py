import whisper
import ollama
import speech_recognition as sr
import os
import pyttsx3

# Load Whisper model (choose"tiny", "base", "small", "medium", or "large")
model = whisper.load_model("small")  # Adjust based on speed vs accuracy

# Initialize text to speech engine
tts_engine = pyttsx3.init()
def record_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nListening... (Say 'exit' to stop)")
        recognizer.adjust_for_ambient_noise(source)    # Reduce background noise
        audio = recognizer.listen(source)

    # Save as a temporary WAV file
    audio_path = "temp_audio.wav"
    with open(audio_path, "wb") as f:
        f.write(audio.get_wav_data())

    return audio_path

# convert audio file to text using whisper
def transcribe_audio(audio_path):
    print("Transcribing audio...")
    result = model.transcribe(audio_path)
    return result ["text"].strip()

# Process text with TinyLlama (Ollama)
def process_text_with_tinyllama(text):
    print("Processing with TinyLlama...")
    response = ollama.chat(model="tinyllama", messages=[{"role": "user", "content": text}])
    return response["message"]["content"]

# Text-to-speech
def text_to_speech(text):
    print(f"TinyLlama Response: {text}")
    tts_engine.say(text)
    tts_engine.runAndWait()

# Main loop for continuous listening
def main(): 
    print("Voice Assistant Started! Say something...\n")
    while True:
        audio_path = record_audio() # capture speech
        transcribed_text = transcribe_audio(audio_path)
        print (f"Text : {transcribed_text}")
        os.remove(audio_path) # Clean up the temp file

        if transcribed_text.lower() == "exit.":
            print ("Exiting...")
            break # Stop the loop if the user says "exit
        
        # response_text = process_text_with_tinyllama(transcribed_text)
        # text_to_speech(response_text)

if __name__ == "__main__":
    main()