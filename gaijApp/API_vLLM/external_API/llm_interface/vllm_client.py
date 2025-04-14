import requests
import time

# You can parameterize this via env vars or config files if needed
MODEL_PATH = "/home/naic-user/Llama-3.2-3B-Instruct"
MODEL_PATH = "/home/gaij/.cache/huggingface/hub/models--meta-llama--Llama-3.2-1b-Instruct/snapshots/9213176726f574b556790deb65791e0c5aa438b6"
ENDPOINT_URL = "http://gaijl4slur-g2gpunodeset-0:8000/v1/completions"
TEMPERATURE = 0.1
MAX_TOKENS = 10000

def send_prompt(prompt_text: str) -> str:
    """Send prompt to vLLM server and return the raw text response."""
    start_time = time.time()

    response = requests.post(
        ENDPOINT_URL,
        json={
            "model": MODEL_PATH,
            "prompt": prompt_text,
            "max_tokens": MAX_TOKENS,
            "temperature": TEMPERATURE
        }
    )

    elapsed = time.time() - start_time
    print(f"[vLLM] Time to process 1 prompt: {elapsed:.2f}s")

    try:
        response.raise_for_status()
        return response.json().get("text", "")
    except Exception as e:
        print(f"[vLLM] Error in response: {e}")
        return None
