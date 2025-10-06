import whisper
import os
import time

audio_path = "out/recorded_audio.wav"

# Load Whisper model (choose"tiny", "base", "small", "medium", or "large")
model = whisper.load_model("small")  # Adjust based on speed vs accuracy

# convert audio file to text using whisper
def transcribe_audio(audio_path):
    print("Transcribing audio...")
    result = model.transcribe(audio_path)
    return result["text"].strip()

def microphone_transcribe():
    print("Voice Assistant Started! Say something...\n")
    # with open(audio_output_file, "w") as f:
    # while True:
    # audio_path = record_audio()
    transcribed_text = transcribe_audio(audio_path)
    print (f"Trascribed text : {transcribed_text}")
    # os.remove(audio_path)
    
    # if transcribed_text.lower() == "exit.":
    #     print("Exiting microphone listener...")
    #     break    

    # if transcribed_text and is_valid_text(transcribed_text):  # Only write if text is not empty
    #     f.write(f"send:{transcribed_text}\n")
    #     f.flush()
    # time.sleep(0.5)

out_dir = "out"
wav_path = os.path.join(out_dir, "recorded_audio.wav")


def operater_main():
    print("hello")
    print(f"Waiting for {wav_path} to be created...")

    # Wait for the file to appear
    while not os.path.exists(wav_path):
        time.sleep(0.5)
    
    prev_size = -1

    while True:
        current_size = os.path.getsize(wav_path)
        if current_size != prev_size:
            microphone_transcribe()
        prev_size = current_size
        time.sleep(0.5)

if __name__ == "__main__":
    operater_main()