"""
Created on Wed Nov 26 2024

"""

# =========================================================================
"""
Goal: run the markdonwfiles through an LLM to extract the important information in a JSON formatted
document, the LLM is run through an API in the server

"""
# =========================================================================

import argparse
import re
import os
import requests
import time
import json
from typing import List


def vLLM_remote(input_dir,out_dir,err_dir,nFiles_r):
    # Main function to run a list of files located in a directory through vLLM 
    #  extract certain data and save it in a JSON format in another directory
    
    # ====== get the list of files to be processed 
    files_list = whichfiles(input_dir,out_dir)
    # ====== Loop through the files and send to server 
    files_loop(files_list,input_dir,out_dir,err_dir,nFiles_r)


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

def files_loop(files_list,input_dir,out_dir,err_dir,nFiles_r):
    # function to loop through the folder with the markdown files (to be processed) and extract 
    # the text from each of them using LLM -- Main function
    
    nFiles = len(files_list)
    if (nFiles_r==-1) | (nFiles<nFiles_r):
        files2Run = nFiles
    else:
        files2Run = nFiles_r
        print(f"{files2Run} files will be processed")
    # count the files saved 
    nSaved = 0
    for i in range(files2Run):
        
        input_file = files_list[i]
        
        # ====== Get the identity of the markdown file 
        input_sep = input_file.split('/')
        id = input_sep[-1][:-3]
        
        # ====== Open the file and read it 
        contextText = readfile(input_dir,input_file)

        #f = open(os.path.join(input_dir,input_file), encoding='UTF-8')   
        #mdText = f.read()
        #plainText = mdText
        #contextText = " {context} " + plainText
        
        print(f"extracting data of file  {i+1}/{files2Run}.....") 
        # ====== get the prompt 
        prompt = make_prompt(contextText)
        # ====== send prompt 
        response = send_prompt(prompt)
        # ====== get the response 
        output = get_response(response)
        # ====== Check the data
            
        if type(output)==str:# data has been extracted 
            
            # ====== transform to JSON and save 
            flagSave = output2json(output,out_dir,err_dir,id)

            if flagSave: # file has been succesfully saved 
                print(f"file  {i+1}/{files2Run} processed :)") 
                nSaved+=1

            else: # file has not been saved 
                 print(f"file  {i+1} with ID {id} has not been saved :(")
            # if output ==-1 problem in the data extraction 

        else:# data has not been extracted
            print(f"file  {i+1} with ID {id} has not been processed :(") 
    
    # ====== print how many files have been saved 
    print(f"  {nSaved} / {files2Run} have been saved") 
        


def readfile(input_dir,input_file):
    # function to open and read the file
     
    f = open(os.path.join(input_dir,input_file), encoding='UTF-8')   
    mdText = f.read()
    plainText = mdText
    contextText = " {context} " + plainText

    return contextText

def make_prompt(contextText):
    # function to create the prompt including the info from the file 

    # ====== Prompt question 
    prompt_question = """
    <|system|> You are a helpful assistant. You process tax records of Norwegian companies and extract specific information from them, then present it in a structured JSON format. 
    This is the tax record you will base your answers on: {content}

    Please return only the response in the following JSON format. Do not include any explanation, comments, or extra information.

    The JSON structure should strictly follow this format:

    {
        "company_name": "string",          
        "company_id": "string",    
        "company_address": "string",        
        "leadership": {
            "CEO": "string or null",       
            "board_members": [
                "string" or null           
            ],
            "chairman_of_the_board": "string or null" 
        },
        "subsidiaries": [
            "string" or null               
        ],
        "parent_company": "string or null", 
        "property_ownership": {
            "owns": [
                "string" or null
            ],
            "rents": [
                "string" or null
            ]   
        },     
        "number_of_employees": "integer or null" ,
        "profit_status": "boolean or null"
    }

    <|user|> Please extract the following information from the tax record:
        
        - "company_name": The name of the company.
        - "company_id": The company tax number.
        - "company_address": The company's address.
        - "leadership": This is a nested dictionary with the following information:
            - "CEO": Name of the CEO.
            - "board_members": List of board members (if available).
            - "chairman_of_the_board": Name of the chairman of the board of the company.
        - "subsidiaries": List of the subsidiaries of the company (empty list if none).
        - "parent_company": Name of the parent company (null if not available).
        - "property_ownership": A dictionary with two lists:
            - "owns": List of properties the company owns (empty list if none).
            - "rents": List of properties the company rents (empty list if none).
        - "number_of_employees": The total number of employees (null if not available).
        - "profit_status": Boolean indicating whether the company made a profit (null if not provided).

    Please ensure that all fields are included, even if they are empty or null.
    Only return the JSON response; do not add explanations, comments, or repeated entries.
    <|assistant|>
    """
    # ====== Complete the prompt 
    prompt_text = contextText + prompt_question

    return prompt_text

def send_prompt(prompt_text):
    # function to send the prompt to the server 
    # Parameters (hard coded) 
        # model_path: path to the model in the server 
        # -- Model parameters 
        # temperature:  stochasticity of the model
        # max_tokens:maximum tokens of the answer 
    # Output:  
        # response of the model 
    
    # ================================================
    
    # ====== About the model
    model_path = '/home/naic-user/Llama-3.2-3B-Instruct'
    temperature=0.1
    max_tokens=10000
    
    # ====== start the time
    start_time = time.time()

    # ====== Sed the prompt 
    response = requests.post(
    "http://localhost:8000/v1/completions",
    json={
        "model": model_path,
        "prompt": prompt_text,
        "max_tokens": max_tokens,
        #"max_model_len": max_model_len,
        "temperature":temperature
        })
    
    # ====== end time 
    end_time = time.time() - start_time
    print(f"time to process 1 file: {end_time}s")
    
    return response

def get_response(response: requests.Response) -> List[str]:
    # function to extract the response of the model

    data = json.loads(response.content)
    try: # check if the response has been created 
        output = data['choices']
        output = output[0]['text']
    except:
        output = -1
    return output

def output2json(output,out_dir,err_dir,id):
    # function to transform the output of the model into a json format and save it 
    #   if the format is not right save it as an error file, 
    #   or a NA file if the file is missing all together 
    
    print(f"saving")
    
    
    # ====== Use regex to extract the JSON block from the response
    json_str_match = re.search(r'{.*}', output, re.DOTALL)
    json_path2save = out_dir + "/" +id+".json"

    if json_str_match:
        json_str = json_str_match.group(0)
        
        # ====== Parse the JSON string
        try: # if the output is in a JSON format 
            json_data = json.loads(json_str)

            # Save the JSON data to a file
            with open(json_path2save, 'w') as json_file:
                json.dump(json_data, json_file, indent=4, ensure_ascii=False)  # Save the JSON with indentation for readability

            print(f"JSON data saved to '{json_path2save}'")
            # Flag that the data has been saved 
            flagSave = 1
           
        
        except json.JSONDecodeError as e: # Error in the spelling
            print(f"Error decoding JSON: {e}")
            # save the id of the file in the error folder 
            errFile = 'er_' + id +'.txt'
            with open(err_dir + '/'+ errFile, "w") as output:
                output.write(str(id))
            flagSave = 0
            
    else: # the output did not procude a file 
        print("No JSON found in the response")
        NAFile = 'na_' + id +'.txt'
        with open(err_dir + '/'+ NAFile, "w") as output:
                output.write(str(id))
        flagSave = 0
    
    return flagSave


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='text data extraction - vllm')
    parser.add_argument('--md_dir', required=False, help='directory with the markdown files to be processed')
    parser.add_argument('--out_dir', required=False, help='Output directory for JSON file ')
    parser.add_argument('--error_dir', required=False, help='Output directory for file wth error files (optional) ')
    parser.add_argument('--run_nFiles', required=False, help='number of Files to run each batch, default -1-> all')

    args = parser.parse_args()
    # ===== get the arguments 
        # input (markdown files)
    if args.md_dir:
        input_dir = args.md_dir
    else:
        input_dir = 'F:\User\markdowns'
        # output ( JSON files)
    if args.out_dir:
        out_dir = args.out_dir
    else:
        out_dir = 'F:\User\JSON
        # error ( txt files)
    if args.out_dir:
        err_dir = args.error_dir
    else:
        err_dir = 'F:\User\errorFiles'
        # number of files to run 
    if args.run_nFiles:
        nFiles_r = int(args.run_nFiles)
    else:
        nFiles_r = -1
    
    
    # Run the main process 
    vLLM_remote(input_dir,out_dir,err_dir,nFiles_r)
    
    
    # process again error files? - defaut False

    
    
    
    
        
    