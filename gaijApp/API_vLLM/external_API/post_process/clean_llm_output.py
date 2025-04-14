import re
import json
import copy

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
    for key, value in data.items():
        cleaned_value = check_empty(value)
        if cleaned_value is not None:
            cleaned[key] = cleaned_value
    return cleaned

def check_empty(value):
    """Cleans out empty or junk values."""
    if isinstance(value, list):
        filtered = [
            v.strip() for v in value
            if isinstance(v, str) and v.strip().lower() not in EMPTY_VALUES
        ]
        return filtered if filtered else None
    elif isinstance(value, str):
        return value.strip() if value.strip().lower() not in EMPTY_VALUES else None
    elif value is None:
        return None
    else:
        return value  # numeric or boolean
