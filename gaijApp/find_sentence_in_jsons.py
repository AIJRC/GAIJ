
import os
import json


def find_sentence_in_jsons(search_sentence, folder_path):
    matching_files = []
    
    # Walk through all files in the folder
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                # Try different encodings
                for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            data = json.load(f)
                            content = json.dumps(data, ensure_ascii=False)
                            
                            if search_sentence in content:
                                matching_files.append(file_path)
                            break  # Successfully read the file, move to next file
                    except UnicodeDecodeError:
                        continue  # Try next encoding
                    except Exception as e:
                        print(f"Error reading {file_path}: {str(e)}")
                        break
    
    return matching_files


if __name__ == "__main__":
    sentence = input("Enter the sentence to search for: ")
    folder = "/Users/nuno/repos/gaij/extracted_oihane"
    
    results = find_sentence_in_jsons(sentence, folder)
    
    if results:
        print("\nFound in following files:")
        for file in results:
            print(file)
    else:
        print("\nSentence not found in any JSON file.")
