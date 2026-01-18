import whisper
import os
import time
from src import node__initial_triage as node__initial_triage
from src import prompts as prompts
from src import llm_utils as llm_utils

audio_path = "out/recorded_audio.wav"

# TODO
# have location check for street number followed by a string.
# refactor so that the initial triage node then leads into more detailed node

# Load Whisper model (choose"tiny", "base", "small", "medium", or "large")
model = whisper.load_model("small")  # Adjust based on speed vs accuracy

out_dir = "out"
wav_path = os.path.join(out_dir, "recorded_audio.wav")

def operator_main():

    llm_utils.text_to_speech("9 1 1 what's your emergency?", out_dir)
    
    # Wait for a recorded audio file to appear
    while not os.path.exists(wav_path):
        time.sleep(0.5)
    

    conversation_state = node__initial_triage.conversation_state
    node__initial_triage.initial_triage_conversation(conversation_state, wav_path, model, audio_path, out_dir)

if __name__ == "__main__":
    operator_main()

