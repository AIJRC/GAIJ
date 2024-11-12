import os
import glob
from transformers import AutoModelForCausalLM, AutoTokenizer


# Specify the path to your LLaMA 3 model directory
model_path = "/Users/nunocalaim/.llama/llama-hf"
model_path = "/home/nuno/GAIJ/llama_32_3b_Instruct"

# Load the tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_path)

# Ensure the pad token is set
if tokenizer.pad_token is None:
    tokenizer.add_special_tokens({'pad_token': tokenizer.eos_token})

model = AutoModelForCausalLM.from_pretrained(model_path)
model.resize_token_embeddings(len(tokenizer))

# Set the pad_token_id and eos_token_id in model configuration
model.config.pad_token_id = tokenizer.pad_token_id
model.config.eos_token_id = tokenizer.eos_token_id

# Print token IDs to confirm they are integers
print("pad_token_id:", model.config.pad_token_id)
print("eos_token_id:", model.config.eos_token_id)

# Make sure eos_token_id and pad_token_id are valid integers
assert isinstance(model.config.pad_token_id, int), "pad_token_id should be an integer."
assert isinstance(model.config.eos_token_id, int), "eos_token_id should be an integer."

def generate_response(prompt):
    # Tokenize the input text and create an attention mask
    inputs = tokenizer(prompt, return_tensors="pt", padding=True)

    # Generate a response using the model
    output = model.generate(
        inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        max_new_tokens=150,
        num_return_sequences=1,
        pad_token_id=model.config.pad_token_id  # Use pad_token_id from the model's config
    )

    # Decode and print the output text
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)

    # Remove the input prompt from the generated response
    generated_text = generated_text[len(prompt):].strip()
    print("Response:", generated_text)

    # Specify the folder containing the markdown files
folder_path = "/home/nuno/GAIJ/converted"

# Use glob to list all .md files in the folder
markdown_files = glob.glob(os.path.join(folder_path, "*.md"))

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        return content

import numpy as np
np.random.seed(2)

file_path = markdown_files[np.random.randint(0, len(markdown_files))]
file_content = read_file(file_path)
# print(file_content)

prompt = f"<|system|> You are a helpful assistant. You process tax-records of norwegian companies and extract information from them. This is the tax-record you will base your answers on {file_content}\n\n you provide your response in JSON format\n<|user|> I want to extract the following information from the tax-record: -company name; -company address; list with names of shareholders; -number of employees; does the company own or rent properties?\n<|assistant|>"

generate_response(prompt)