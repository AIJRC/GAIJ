import json
import os
import sys
from tqdm import tqdm
import pandas as pd

from external_apis.external_apis import run_all_external_apis
from prompt_template.build_prompt import build_prompt
from llm_interface.vllm_client import send_prompt
from post_process.clean_llm_output import clean_llm_output

def read_company_ids(csv_path):
    try:
        df = pd.read_csv(csv_path)
        company_ids = df['company_id'].dropna().astype(str).tolist()
        print(f"[INFO] Successfully read {len(company_ids)} company IDs.")
        return company_ids
    except Exception as e:
        print(f"[ERROR] Failed to read company_id column from CSV: {e}")
        return []

def already_processed(company_id, output_dir):
    file_path = os.path.join(output_dir, f"{company_id}_external.json")
    exists = os.path.isfile(file_path)
    if exists:
        print(f"[SKIP] {company_id} already processed. Skipping.")
    return exists

def save_json(data, output_dir, company_id):
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{company_id}_external.json")
    try:
        with open(out_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"saved {data}")    
        print(f"[SUCCESS] Saved cleaned output to {out_path}")
    except Exception as e:
        print(f"[ERROR] Could not save JSON for {company_id}: {e}")

# -------- MAIN --------
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main.py <path/to/company_ids.csv> <output/folder>")
        sys.exit(1)

    csv_path, output_dir = sys.argv[1], sys.argv[2]
    company_ids = read_company_ids(csv_path)

    print(f"[START] Processing {len(company_ids)} company IDs...")

    for company_id in tqdm(company_ids):
        print(f"\n[PROCESSING] Company ID: {company_id}")

        if already_processed(company_id, output_dir):
            continue

        print(f"[INFO] Calling external APIs for {company_id}")
        raw_api_output = run_all_external_apis(company_id)
        if not raw_api_output:
            print(f"[WARNING] No data returned from external APIs for {company_id}. Skipping.")
            continue

        print(f"[INFO] Building prompt for {company_id}")
        prompt = build_prompt(raw_api_output)

        print(f"[INFO] Sending prompt to LLM for {company_id}: {prompt}")
        vllm_response = send_prompt(prompt)
        if not vllm_response:
            print(f"[ERROR] No response from LLM for {company_id}. Skipping.")
            continue

        print(f"[INFO] Cleaning LLM output for {company_id}")
        structured_output = clean_llm_output(vllm_response)

        save_json(structured_output, output_dir, company_id)

    print("\n[COMPLETE] All company IDs processed.")

