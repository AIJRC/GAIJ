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
        return df['company_id'].dropna().astype(str).tolist()
    except Exception as e:
        print(f"Error reading company_id column: {e}")
        return []

def already_processed(company_id, output_dir):
    file_path = os.path.join(output_dir, f"{company_id}_external.json")
    return os.path.isfile(file_path)


def save_json(data, output_dir, company_id):
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, f"{company_id}_external.json"), 'w') as f:
        json.dump(data, f, indent=2)

# -------- MAIN --------

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main.py <path/to/company_ids.csv> <output/folder>")
        sys.exit(1)

    csv_path, output_dir = sys.argv[1], sys.argv[2]
    company_ids = read_company_ids(csv_path)

    print(f"Found {len(company_ids)} company IDs to process.")

    for company_id in tqdm(company_ids):
        if already_processed(company_id, output_dir):
            continue

        raw_api_output = run_all_external_apis(company_id)
        if not raw_api_output:
            continue

        prompt = build_prompt(raw_api_output)
        vllm_response = send_prompt(prompt)
        if not vllm_response:
            continue

        structured_output = clean_llm_output(vllm_response)
        save_json(structured_output, output_dir, company_id)
