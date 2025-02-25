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
from transformers import AutoModelForCausalLM, AutoTokenizer



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
        # ====== set the model
        [tokenizer,model] = set_model()
        # ====== send the prompt and get the response 
        output = get_response(tokenizer,model,prompt)
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
    # Load the tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path,n_gpu_layers=-1)

    # Check if eos_token is defined; if not, set it to a valid special token
    if tokenizer.eos_token is None:
        # Define a special token if needed
        tokenizer.add_special_tokens({'eos_token': '</s>'})  # Use a default end-of-sequence token

    # Ensure the pad token is set
    if tokenizer.pad_token is None:
        tokenizer.add_special_tokens({'pad_token': tokenizer.eos_token})

    # Reload the model and resize the embeddings to account for the new pad token
    model = AutoModelForCausalLM.from_pretrained(model_path)
    model.resize_token_embeddings(len(tokenizer))

    # Set the pad_token_id and eos_token_id in model configuration
    model.config.pad_token_id = tokenizer.pad_token_id
    model.config.eos_token_id = tokenizer.eos_token_id

    # Print token IDs to confirm they are integers
    #print("pad_token_id:", model.config.pad_token_id)
    #print("eos_token_id:", model.config.eos_token_id)

    # Make sure eos_token_id and pad_token_id are valid integers
    assert isinstance(model.config.pad_token_id, int), "pad_token_id should be an integer."
    assert isinstance(model.config.eos_token_id, int), "eos_token_id should be an integer."
    
    return [tokenizer,model]

def get_response(tokenizer,model,input_text): 
    # Tokenize the input text and create an attention mask
    inputs = tokenizer(input_text, return_tensors="pt", padding=True)

    # Generate a response using the model
    output = model.generate(
        inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        max_new_tokens=300,
        num_return_sequences=1,
        pad_token_id=model.config.pad_token_id  # Use pad_token_id from the model's config
    )

    # Decode and print the output text
    # select only the outcome 
    prompt_tokens = tokenizer(input_text, return_tensors="pt")["input_ids"]
    start_index = prompt_tokens.shape[-1]
    generation_output = output[0][start_index:]
    try:
        generated_text = tokenizer.decode(generation_output, skip_special_tokens=True)
    except:
        generated_text = -1
    
    print(generated_text)
    
    return generated_text