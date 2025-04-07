"""
Interface to load the required documents     
"""

import os
import json


outputadd = "\\JSON_notes\\"

def whichfiles(out_dir,input_format,output_format):
    # function to extract the list of files that still need to be processed
    """ modified so it lists of the already processed files to add """
    
    # ===  make sure the directories exist 
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(out_dir+ outputadd, exist_ok=True)
    # ==== List tje JSON and MD files 
    json = list(filter(lambda x: x.endswith(output_format), os.listdir(out_dir)))
    markdown = list(filter(lambda x: x.endswith(output_format), os.listdir(out_dir)))
    # ==== Find all files to be procesed ( that have not been processed yet)
    files_list = list(set(markdown).difference(set(map(lambda x: os.path.splitext(x)[0] + output_format+outputadd, json))))
    # change the outfor to the input format 
    files2proces = [re.sub(output_format,input_format,file) for file in files_list]
    
    print(f"{len(files2proces)} files found, example file: {files2proces[0]}")
    
    return(files2proces)


def readfile(input_dir,input_file):
    # function to open and read the file - includes the step of removing any line that does not start with letters ( including norwegian alphabet)
     
    f = open(os.path.join(input_dir,input_file), encoding='UTF-8')   
    mdText = f.read()
    plainText = mdText

    contextText = " {context} " + plainText

    return contextText

    

def savejson(json_data,json_path,id):
    " save the JSON file checking whether another one already exits and if so updating it"
    json_path2save = f'{json_path}{outputadd}{id}.json'
    json_pathFile = f'{json_path}\\{id}.json'
    print(json_pathFile)
    # check wether a file with the name exists
    if os.path.exists(json_pathFile):
        # load the existing data 
        with open(json_pathFile, 'r') as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = {}
        # Ensure it's a dictionary before merging
        if isinstance(existing_data, dict) and isinstance(json_data, dict):
            existing_data.update(json_data)
        else:
            print("Error: Existing data is not a dictionary. Overwriting.")
            existing_data = json_data
            
    else:
         print("Warning: No previous data found")
         existing_data = json_data


    # Save the JSON data to a file
    with open(json_path2save, 'w') as json_file:
        json.dump(existing_data, json_file, indent=4, ensure_ascii=False)  # Save the JSON with indentation for readability

    print(f"JSON data saved to '{json_path2save}'")
    
    
def saveInference(inference,out_dir):
    # ======== Save as text the inference block of the response 
    
    text_path = out_dir + "\\inference\\"
    # check the folder exist
    if not os.path.isdir(text_path):
        os.mkdir(text_path)
    text_path2save = f'{text_path}{id}.txt'
    # check whether the file already exist 
    if os.path.exists(text_path2save):
        # open the text 
        try:
            f = open(text_path2save,'r')
            content = f.read()
            # update the content 
            new_conten = content + inference
        except TypeError:
            print("Error: Existing data does not exist. Overwriting.")
            new_conten = copy.copy(inference)
    else: 
        new_conten = copy.copy(inference)
            
    print("Saving the inference of the document")
    with open(text_path2save, "w") as text:
        text.write(new_conten)