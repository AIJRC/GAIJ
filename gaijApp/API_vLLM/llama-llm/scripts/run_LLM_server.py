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
import requests
import time
import json
from typing import List
from prompts.prompt_manager import make_prompt
from documents.document_manager import readfile
from utils.support_functions import DotDict,get_fields
from processing.response_parser import output2json



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
    


    
