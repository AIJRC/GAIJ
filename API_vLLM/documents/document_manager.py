"""
Interface to load the required documents     
"""

import os
import json


def whichfiles(input_dir,out_dir):
    # function to extract the list of files that still need to be processed
    
    # ======  make sure the directories exist 
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)
    # ====== List tje JSON and MD files 
    json = list(filter(lambda x: x.endswith(".json"), os.listdir(out_dir)))
    markdown = list(filter(lambda x: x.endswith(".md"), os.listdir(input_dir)))
    # ====== Find all files to be procesed ( that have not been processed yet)
    files_list = list(set(markdown).difference(set(map(lambda x: os.path.splitext(x)[0] + ".md", json))))
    
    
    print(f"{len(files_list)} files found, example file: {files_list[0]}")
    
    return(files_list)


def readfile(input_dir,input_file):
    # function to open and read the file
     
    f = open(os.path.join(input_dir,input_file), encoding='UTF-8')   
    mdText = f.read()
    plainText = mdText
    contextText = " {context} " + plainText

    return contextText

def save_JSON(json_data,json_path2save):
    # Save the JSON data to a file
    with open(json_path2save, 'w') as json_file:
        json.dump(json_data, json_file, indent=4, ensure_ascii=False)  # Save the JSON with indentation for readability
        print(f"JSON data saved to '{json_path2save}'")
        # Flag that the data has been saved 
        flagSave = 1
    return flagSave

def save_text(fileName,variable):
    # save a variable (str) to a text file 
    with open(fileName, "w") as output:
            output.write(variable)
            flagSave = 0
    return flagSave