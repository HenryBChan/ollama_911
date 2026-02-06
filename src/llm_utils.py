import subprocess
import json
import re
import gc
from typing import Optional

def clean_llm_output(text: str) -> str:
    ANSI_ESCAPE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
    # Remove ANSI escape codes
    text = ANSI_ESCAPE.sub("", text)

    # Remove markdown code fences
    text = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE)

    return text.strip()


def query_llm(user_message, current_state, prompt_body):
    # HARD truncate user input (critical)
    user_message = user_message[:500]

    # Keep prompt extremely small
    prompt = (
        prompt_body
        + f'Text: "{user_message}"\n'
        + "JSON:"
    )

    try:
        result = subprocess.run(
            ["ollama", "run", "gemma2:2b", prompt],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=120
        )

        # "model": "mistral",       # requires 4.5 Gb mem
        # "model": "phi3:3.8b",
        # "model": "tinyllama:1.1b",
        # "model": "phi3:mini",       # requires more mem
        # "model": "gemma2:2b",

        raw_output = clean_llm_output(result.stdout)
        print(f"raw_output {raw_output}")
    except subprocess.TimeoutExpired:
        print("⏱ Ollama subprocess timed out")
        return current_state.copy()

    except Exception as e:
        print("❌ Ollama request failed:", e)
        return current_state.copy()

    # Immediately drop references we no longer need
    del result
    # del data
    gc.collect()

    # Parse JSON safely
    try:
        match = re.search(r"\{.*\}", raw_output, re.DOTALL)
        if not match:
            return current_state.copy()

        parsed = json.loads(match.group(0))

        schema_line = prompt_body.strip().splitlines()[-1]
        keys = json.loads(schema_line).keys()

        return {
            key: parsed.get(key, current_state.get(key))
            for key in keys
        }

    except Exception:
        return current_state.copy()
    
# Text-to-speech
def text_to_speech(text, out_dir):
    print(f"Operator Response: {text}")
    with open(f"{out_dir}/operator_voice.txt", "w", encoding="utf-8") as f:
        f.write(text)


# def detect_yes_no(text):
#     if isinstance(text, bool):
#         return True
#     if not isinstance(text, str):
#         return False
#     text = text.lower().strip()
#     return text in ("yes", "no")

def normalize_yes_no(value):
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, str):
        v = value.lower().strip()
        if v in ("yes", "no"):
            return v
    return None