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
from llama_cpp import Llama



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
    


def set_model():
    # ====== About the model
    model_path = '/home/naic-user/Llama-3.2-3B-Instruct'
    temperature=0.1
    llm = Llama(model_path=model_path,n_gpu_layers=-1, n_ctx=10000, verbose = False, chat_format="chatml",temperature=temperature) 

    return llm

def get_response(llm,prompt_question): 
    output = llm.create_chat_completion(messages=prompt_question,temperature =0)
                        
    # Get the response 
    try:
        generated_text = output["choices"][0]["message"]
    except:
        generated_text = -1
    print(generated_text)
    return generated_text
    
