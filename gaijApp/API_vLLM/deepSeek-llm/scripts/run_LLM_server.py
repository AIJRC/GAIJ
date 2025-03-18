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

import re
import requests
import time
import json
from typing import List
from prompts.prompt_manager import prompt_rf_v2,prompt_data
from documents.document_manager import readfile
from utils.support_functions import DotDict,get_fields
from processing.response_parser import output2json



def files_loop(files_list,input_dir,out_dir,nFiles_r,prmpt_settings,prmpt_info_settings):
    # function to loop through the folder with the markdown files (to be processed) and extract 
    # the text from each of them using LLM -- Main function
    
    nFiles = len(files_list)
    if (nFiles_r==-1) | (nFiles<nFiles_r):
        files2Run = nFiles
    else:
        files2Run = nFiles_r
        print(f"{files2Run} files will be processed")
    for i in range(files2Run):
        
        input_file = files_list[i]
        
        # ========= Get the identity of the markdown file 
        input_sep = input_file.split('/')
        id = input_sep[-1][:-3]
        
        # ======= Open the file and read it 
        contextText = readfile(input_dir,input_file)
        
        
        
        # get the type of data that needs to be extracted 
        
        if prmpt_settings.info_Flag:
            # extract the information of the file
            print(f"extracting information of file  {i+1}/{files2Run}.....")  
        if prmpt_settings.notes_Flag: 
            # extract the summary of the file
            print(f"extracting summary of notes of file  {i+1}/{files2Run}.....")  
        if prmpt_settings.redFlags_Flag: 
            # extract the red flags from the file 
            print(f"extracting red flags of file  {i+1}/{files2Run}.....") 
            
        
        # get notes prompt
        flag_saveInference = False
        notes_prompt,system_notesPrompt = prompt_rf_v2()
        # ==== send prompt 
        response = send_prompt(notes_prompt+contextText,system_notesPrompt)
        
        # ====== get the response 
        output = get_response(response)
    
        print(output)
            # data has been extracted 
        
        if type(output)==str:
           # ====== transform to JSON and save and translate 
            
            [json_data,inference] = output2json(output,out_dir)
            if json_data is not None: 
                # ==== translate the data 
                json_dataENG = translate_json(json_data)
                
                # === save the data 
                print("savind the extracted data of the file")
                if isinstance(json_dataENG, dict):
                    savejson(json_dataENG,out_dir,id)
            if flag_saveInference:
                saveInference(inference,out_dir)
            print(f"file  {i+1}/{files2Run} processed :)") 
            # if output ==-1 problem in the data extraction 
        else:
           print(f"file  {i+1} with ID {id} notes have not been processed :(") 
    
    # ====== print how many files have been saved 
    print(f"  {nSaved} / {files2Run} have been saved") 
    # print the fields that have be extracted in the last file 
    if (i+1)==files2Run: 
        reqst_fields= get_fields(prmpt_info_settings)
        print(f"extracted the fields: {" ".join(reqst_fields)}")
    

def send_prompt(user_prompt,system_prompt):
    # function to send the prompt to the server 
    # Parameters (hard coded)
        # prompt_question: base prompt question 
        # model_path: path to the model in the server 
        # -- Model parameters 
        # temperature:  stochasticity of the model
        # min_tokens and max_tokens: min and maximum tokens of the anser 
    # Output:  
        # response of the model 
    
    # ================================================
    # ===== Prompt question 
    
    # =========================== About the model
    #model_path = '/home/naic-user/Llama-3.2-3B-Instruct'
    model_path = 'deepseek-ai/DeepSeek-R1-Distill-Llama-8B'
    temperature=0.0
    #temperature = 0.7
    #max_tokens=10000
    max_tokens=2000
    
    
        # start the time
    start_time = time.time()

    # =============== Sed the prompt 
    response = requests.post(
    #"http://localhost:8000/v1/completions",
    "http://localhost:8000/v1/chat/completions",
    json={
        "model": model_path,
        #"prompt": prompt_text,
        'messages':[{'role': "system","content": system_prompt}, #   # prompt_system
                   {"role": "user","content": user_prompt}], #  contextText
        "max_tokens": max_tokens,
        #"max_model_len": max_model_len,
        "temperature":temperature,
        })
    
        # end time 
    end_time = time.time() - start_time
    print(f"time to process 1 file: {end_time}s")
    
    # ===== get the answer 
    return response

def get_response(response: requests.Response) -> List[str]:

    
    # function to extract the response of the model

    data = json.loads(response.content)
    
    #print(data)
    try:
        output = data['choices'][0]['message']['content']
        #output = output[0]['text']
        #output = data[0]['choices']#['content']
        
    except:
        output = -1
    return output
    

    

def run_extractInfo(contextText,out_dir,prmpt_info_settings):
    " script that run the necesary steps to extract and save the data "
    
    flag_saveInference = True
    notes_prompt,system_notesPrompt = prompt_data()
    # ==== send prompt 
    response = send_prompt(notes_prompt,system_notesPrompt)
        
    # ====== get the response 
    output = get_response(response)
    # get the JSON of the response 
    if type(output)==str:
           # ====== transform to JSON and save and translate 
            
            [json_data,inference] = output2json(output,out_dir)
            if json_data is not None: 
                json_data = json.loads(json_data)
            
                # cleand the data and make it into an standardized structure
                cleanded_JSON = get_standardStructure(json_data,prmpt_info_settings)
            
                # add version control 
                cleaned_JSON_ver = add_versioncontrol(cleanded_JSON,notes_prompt+system_notesPrompt)

                # Save the JSON data to a file
                flagSave = save_JSON(cleaned_JSON_ver,out_dir)
    