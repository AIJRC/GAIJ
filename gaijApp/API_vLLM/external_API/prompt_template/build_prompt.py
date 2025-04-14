import os

def load_template(template_path="prompt_template/template.txt"):
    with open(template_path, "r") as f:
        return f.read()

def build_prompt(api_data: str, template_path="prompt_template/template.txt") -> str:
    template = load_template(template_path)
    return template.replace("{{api_data}}", api_data.strip())
