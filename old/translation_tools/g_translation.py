from googletrans import Translator
import os
import sys
import time

# Initialize translator
translator = Translator()


def split_into_chunks(text, chunk_size=5000):
    chunks = []
    current_pos = 0
    
    while current_pos < len(text):
        if current_pos + chunk_size >= len(text):
            chunks.append(text[current_pos:])
            break
            
        # Find the last space before chunk_size
        split_pos = text.rfind(' ', current_pos, current_pos + chunk_size)
        if split_pos == -1:
            split_pos = current_pos + chunk_size
            
        chunks.append(text[current_pos:split_pos])
        current_pos = split_pos + 1
        
    return chunks

def translate_markdown_file(file_path):
    translator = Translator()
    
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    # Split text into chunks
    chunks = split_into_chunks(text)
    
    # Translate each chunk
    translated_chunks = []
    for chunk in chunks:
        translated = translator.translate(chunk, src='no', dest='en')
        translated_chunks.append(translated.text)
        time.sleep(1)  # Small delay between chunks to avoid rate limiting
        
    # Combine translated chunks
    translated_text = ' '.join(translated_chunks)

    # Save the translated text
    new_file_path = f"translated_{os.path.basename(file_path)}"
    with open(new_file_path, 'w', encoding='utf-8') as new_file:
        new_file.write(translated_text)


# Check if folder path is provided as a command-line argument
if len(sys.argv) < 2:
    print("Please provide the folder path as an argument.")
    sys.exit(1)

# Get the folder path from the command-line argument
folder_path = sys.argv[1]

# Ensure the folder exists
if os.path.isdir(folder_path):
    # Iterate through all markdown files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.md'):
            file_path = os.path.join(folder_path, file_name)
            translate_markdown_file(file_path)
else:
    print("The provided folder path does not exist.")
    sys.exit(1)