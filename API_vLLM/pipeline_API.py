"""
Created on Tue Dec 10 2024

"""

# =========================================================================
"""
Goal: run the markdonwfiles through an LLM to extract the important information in a JSON formatted
document, the LLM is run through an API in the server
     This is the main component of the pipeline which inculdes
     - Getting the input
     - Selecting the right prompt 
     - Run the API 
     - Clean the output and save it 

"""
# =========================================================================

import argparse
import re
import os
import requests
import time
import json
from prompt_API import mk_prompt,get_fields
from clean_output_API import get_standardStructure 
from typing import List


def vLLM_remote(input_dir,out_dir,err_dir,nFiles_r,prmpt_settings):
    # Main function to run a list of files located in a directory through vLLM 
    #  extract certain data and save it in a JSON format in another directory
    
    # ====== get the list of files to be processed 
    files_list = whichfiles(input_dir,out_dir)
    # ====== Loop through the files and send to server 
    files_loop(files_list,input_dir,out_dir,err_dir,nFiles_r,prmpt_settings)


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

def files_loop(files_list,input_dir,out_dir,err_dir,nFiles_r,prmpt_settings):
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
        # print the fields that will be extracted in the first file 
        if i==0: 
            reqst_fields= get_fields(prmpt_settings)
            print(f"requesting the fields: {" ".join(reqst_fields)}")
            
        print(f"extracting data of file  {i+1}/{files2Run}.....") 
        
            
        # ====== get the prompt 
        prompt = make_prompt(contextText,prmpt_settings)
        # ====== send prompt 
        response = send_prompt(prompt)
        # ====== get the response 
        output = get_response(response)
        # ====== Check the data
            
        if type(output)==str:# data has been extracted 
            
            # ====== transform to JSON and save 
            flagSave = output2json(output,out_dir,err_dir,id,prmpt_settings)

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
    # print the fields that have be extracted in the last file 
    if (i+1)==files2Run: 
        reqst_fields= get_fields(prmpt_settings)
        print(f"extracted the fields: {" ".join(reqst_fields)}")
    
        


def readfile(input_dir,input_file):
    # function to open and read the file
     
    f = open(os.path.join(input_dir,input_file), encoding='UTF-8')   
    mdText = f.read()
    plainText = mdText
    contextText = " {context} " + plainText

    return contextText


def make_prompt(contextText,prmpt_settings):
    # function to create the prompt including the info from the file 

    # ====== Prompt question 
    prompt_question=mk_prompt(prmpt_settings)
        # To do: print the fields that are being extracted and the language 
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

def save_JSON(json_data,json_path2save):
    # Save the JSON data to a file
    with open(json_path2save, 'w') as json_file:
        json.dump(json_data, json_file, indent=4, ensure_ascii=False)  # Save the JSON with indentation for readability
        print(f"JSON data saved to '{json_path2save}'")
        # Flag that the data has been saved 
        flagSave = 1
    return flagSave
        
    


def output2json(output,out_dir,err_dir,id,prmpt_settings):
    # function to transform the output of the model into a json format and save it in a
    # standardized form 
    #   if the format is not right save it as an error file, 
    #   or a NA file if the file is missing all together 
    
    print(f"cleaning and saving")
    
    
    # ====== Use regex to extract the JSON block from the response
    json_str_match = re.search(r'{.*}', output, re.DOTALL)
    json_path2save = out_dir + "/" +id+".json"

    if json_str_match:
        json_str = json_str_match.group(0)
        
        # ====== Parse the JSON string
        try: # if the output is in a JSON format 
            json_data = json.loads(json_str)
            
            # cleand the data and make it into an standardized structure
            cleanded_JSON = get_standardStructure(json_data,prmpt_settings)

            # Save the JSON data to a file
            flagSave = save_JSON(cleanded_JSON,json_path2save)
           
        
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


class DotDict(dict):
    """A dictionary that supports dot notation."""
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        del self[key]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='text data extraction - vllm')
    # General settings 
    parser.add_argument('--md_dir', required=False, help='directory with the markdown files to be processed')
    parser.add_argument('--out_dir', required=False, help='Output directory for JSON file ')
    parser.add_argument('--error_dir', required=False, help='Output directory for file wth error files (optional) ')
    parser.add_argument('--run_nFiles', required=False, help='number of Files to run each batch, default -1-> all')
    # Prompt settings 
    parser.add_argument('--NOR_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask for the prompt to be in Norwegian - default FALSE')
    parser.add_argument('--AllFields_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask to select all the information files of the prompt - default TRUE')
    parser.add_argument('--name_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask to extract the Name of the company - default TRUE only available if AllFields_Flag==FALSE')
    parser.add_argument('--id_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask to extract the ID of the company - default TRUE only available if AllFields_Flag==FALSE')
    parser.add_argument('--adrs_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask to extract the Address of the company - default TRUE only available if AllFields_Flag==FALSE')
    parser.add_argument('--typ_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask to extract the Type of company - default TRUE only available if AllFields_Flag==FALSE')
    parser.add_argument('--lead_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask to extract the Leadership of the company - default TRUE only available if AllFields_Flag==FALSE')
    parser.add_argument('--subs_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask to extract the subsidiaries of the company - default TRUE only available if AllFields_Flag==FALSE')
    parser.add_argument('--parnt_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask to extract the Parent company of the company - default TRUE only available if AllFields_Flag==FALSE')
    #parser.add_argument('--id_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask to extract the ID of the company - default TRUE only available if AllFields_Flag==FALSE')
    
    args = parser.parse_args()
    # ===== get the arguments - General settings
        # input (markdown files)
    if args.md_dir:
        input_dir = args.md_dir
    else:
        input_dir = 'F:\\Oihane\\OsloMet\\data\\markdown\\markdowns'
        #input_dir = 'F:\\Oihane\\OsloMet\\data\\markdown\\check_Lang'
        # input_dir = 'F:\User\markdowns'
        # output ( JSON files)
    if args.out_dir:
        out_dir = args.out_dir
    else:
        out_dir = 'F:\\Oihane\\OsloMet\\data\\JSON\\ENG_prompt'
        #out_dir = 'F:\\Oihane\\OsloMet\\data\\JSON\\NOR_prompt'
        #out_dir = 'F:\\Oihane\\OsloMet\\data\\JSON\\check_Lang\\NOR'
        #out_dir = 'F:\\Oihane\\OsloMet\\data\\JSON\\check_Lang\\ENG'
        # out_dir = 'F:\User\JSON
        # error ( txt files)
    if args.out_dir:
        err_dir = args.error_dir
    else:
        err_dir = 'F:\\Oihane\\OsloMet\\data\\errorFiles_oihane\\new_prompt'
        # err_dir = 'F:\User\errorFiles'
        # number of files to run 
    if args.run_nFiles:
        nFiles_r = int(args.run_nFiles)
    else:
        nFiles_r = -1
        
    # ===== get the arguments - prompt settings
    # Create a prompt setting arguments that supports dot notation 
    prmpt_settings = DotDict()    
    
    # ===== get the arguments 
        # Flag for the prompt to be in NORWEGIAN 
    if args.NOR_Flag is not None:
        prmpt_settings.NOR_Flag = args.NOR_Flag
    else:
        prmpt_settings.NOR_Flag = False
        # Flag to extract all the possible data fields 
    if args.AllFields_Flag is not None:
        prmpt_settings.AllFields_Flag = args.AllFields_Flag  
    else:
        prmpt_settings.AllFields_Flag = True

        # IF only some fields are needed 
    if prmpt_settings.AllFields_Flag == False: 
         
            # Flag to extract Name
        if args.name_Flag is not None:
            prmpt_settings.name_Flag = args.name_Flag
        else:
            prmpt_settings.name_Flag = False
        
            # Flag to extract ID
        if args.id_Flag is not None:
            prmpt_settings.id_Flag = args.id_Flag
        else:
            prmpt_settings.id_Flag = False
            # Flag to extract Address
        if args.adrs_Flag is not None:
            prmpt_settings.adrs_Flag = args.adrs_Flag
        else:
            prmpt_settings.adrs_Flag = False
            # Flag to extract Type of company
        if args.typ_Flag is not None:
            prmpt_settings.typ_Flag = args.typ_Flag
        else:
            prmpt_settings.typ_Flag = False
            # Flag to extract Leadership of the company
        if args.lead_Flag is not None:
            prmpt_settings.lead_Flag = args.lead_Flag
        else:
            prmpt_settings.lead_Flag = False
            # Flag to extract Subsidiaries
        if args.subs_Flag is not None:
            prmpt_settings.subs_Flag = args.subs_Flag
        else:
            prmpt_settings.subs_Flag = False
            # Flag to extract Parent Company
        if args.parnt_Flag is not None:
            prmpt_settings.parnt_Flag = args.parnt_Flag
        else:
            prmpt_settings.parnt_Flag = False
        #    # Flag to extract Name
        #if args.name_Flag is not None:
        #    name_Flag = args.name_Flag
        #else:
        #    name_Flag = False
    else: 
        # All of the data fields are true 
        prmpt_settings.name_Flag = True
        prmpt_settings.id_Flag = True
        prmpt_settings.adrs_Flag = True
        prmpt_settings.typ_Flag = True
        prmpt_settings.lead_Flag = True
        prmpt_settings.subs_Flag = True
        prmpt_settings.parnt_Flag= True
    
    
    # Run the main process 
    vLLM_remote(input_dir,out_dir,err_dir,nFiles_r,prmpt_settings)
    
    
    # process again error files? - defaut False

    
    
    
    
        
    