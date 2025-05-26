import re
import json
import os
import sys

EMPTY_VALUES = {
    'null', 'none', 'nan', 'string', 'string or null', 'integer or null',
    'boolean or null', 'n/a', 'no data available', '', 'unknown', '---', 'nei'
}

def clean_llm_output(raw_response: str) -> dict:
    """
    Extracts and cleans a JSON object from raw LLM output.
    Falls back to raw output if JSON is invalid.
    """
    match = re.search(r'{.*}', raw_response, re.DOTALL)
    if not match:
        return {"raw_output": raw_response.strip()}

    try:
        parsed = json.loads(match.group(0))
        return clean_fields(parsed)
    except json.JSONDecodeError:
        return {"raw_output": raw_response.strip()}

def clean_fields(data: dict) -> dict:
    cleaned = {}
    leadership_names = set()

    for key, value in data.items():
        if key.lower() == "leadership":
            cleaned_value = check_empty(value)
            if isinstance(cleaned_value, dict):
                for role, names in cleaned_value.items():
                    names = check_empty(names)
                    if names:
                        if isinstance(names, list):
                            leadership_names.update(names)
                        else:
                            leadership_names.add(names)
            elif isinstance(cleaned_value, list):
                leadership_names.update(cleaned_value)
            elif isinstance(cleaned_value, str):
                leadership_names.add(cleaned_value)
        else:
            cleaned_value = check_empty(value)
            if cleaned_value is not None:
                cleaned[key] = cleaned_value

    if leadership_names:
        cleaned["leadership"] = sorted(leadership_names)

    return cleaned

def check_empty(value):
    """Recursively cleans out empty or junk values."""
    if isinstance(value, dict):
        cleaned = {k: check_empty(v) for k, v in value.items()}
        cleaned = {k: v for k, v in cleaned.items() if v is not None}
        return cleaned if cleaned else None
    elif isinstance(value, list):
        cleaned = [check_empty(v) for v in value]
        cleaned = [v for v in cleaned if v is not None]
        return cleaned if cleaned else None
    elif isinstance(value, str):
        stripped = value.strip()
        return stripped if stripped.lower() not in EMPTY_VALUES else None
    elif value is None:
        return None
    else:
        return value


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <folder_path>")
        sys.exit(1)

    folder_path = sys.argv[1]

    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a valid directory")
        sys.exit(1)

    for fname in os.listdir(folder_path):
        if fname.endswith(".json"):
            path = os.path.join(folder_path, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                print(data)
                cleaned = clean_fields(data)
                print(f"Cleaned {fname}:")
                print(json.dumps(cleaned, indent=2, ensure_ascii=False))
                print(cleaned)
            except Exception as e:
                print(f"Failed to process {fname}: {e}")