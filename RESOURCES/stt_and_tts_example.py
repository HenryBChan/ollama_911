import whisper
import ollama
import speech_recognition as sr
import os
import pyttsx3
import multiprocessing
import time
import re

audio_output_file = "microphone_capture.txt"

# Load Whisper model (choose"tiny", "base", "small", "medium", or "large")
model = whisper.load_model("small")  # Adjust based on speed vs accuracy

# Initialize text to speech engine
tts_engine = pyttsx3.init()

def record_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nListening... (Say 'exit' to stop)")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    # Save as a temporary WAV file
    audio_path = "temp_audio.wav"
    with open(audio_path, "wb") as f:
        f.write(audio.get_wav_data())
    return audio_path

def is_valid_text(text):
    return bool(re.match(r'^[a-zA-Z0-9 .,!?"\'-]+$', text))

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

def microphone_listener():
    print("Voice Assistant Started! Say something...\n")
    with open(audio_output_file, "w") as f:
        while True:
            audio_path = record_audio()
            result = model.transcribe(audio_path)
            transcribed_text = result["text"].strip()
            print (f"Trascribed text : {transcribed_text}")
            os.remove(audio_path)
            
            if transcribed_text.lower() == "exit.":
                print("Exiting microphone listener...")
                break    

            if transcribed_text and is_valid_text(transcribed_text):  # Only write if text is not empty
                f.write(f"send:{transcribed_text}\n")
                f.flush()
            time.sleep(0.5)

def text_processor():
    while True:
        time.sleep(1)  # Prevents high CPU usage

        if os.path.exists(audio_output_file):
            processed_lines = []

            with open(audio_output_file, "r") as f:
                lines = f.readlines()

            with open(audio_output_file, "w") as f:
                for line in lines:
                    if line.startswith("send:"):
                        text = line.replace("send:", "").strip()
                        if text:  # Process only non-empty lines
                            response_text = process_text_with_tinyllama(text)
                            text_to_speech(response_text)
                            processed_lines.append(f"processed:{text}\n")  # Store processed lines
                    else:
                        processed_lines.append(line)  # Keep already processed lines
                
                f.writelines(processed_lines)  # Write back the updated lines



def main():
    p1 = multiprocessing.Process(target=microphone_listener)
    p2 = multiprocessing.Process(target=text_processor)
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.terminate()

if __name__ == "__main__":
    main()
