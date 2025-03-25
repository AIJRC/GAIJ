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
from prompts.prompt_manager import make_prompt, make_external_prompt
from documents.document_manager import readfile
from external_apis.external_apis import run_all_external_apis
from utils.support_functions import DotDict,get_fields
from processing.response_parser import output2json
from transformers import AutoModelForCausalLM, AutoTokenizer
from vllm import LLM, SamplingParams
from vllm.distributed.parallel_state import destroy_model_parallel
import torch
import torch.distributed as dist
import gc
import os 
import psutil


def files_loop(files_list,input_dir,out_dir,ext_dir,err_dir,nFiles_r,prmpt_settings):
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
    
    # ====== set the model
    #[tokenizer,model] = set_model()
    # using vllm
    [llm, sampling_params] = set_model_vllm()
    for i in range(files2Run):
        
        input_file = files_list[i]
        
        # ====== Get the identity of the markdown file 
        input_sep = input_file.split('/')
        id = input_sep[-1][:-3]
        
        # ====== Open the file and read it 
        contextText = readfile(input_dir,input_file)


        if i==0: 
            reqst_fields= get_fields(prmpt_settings)
            print(f'requesting the fields: {" ".join(reqst_fields)}')
            
        print(f'extracting data of file  {i+1}/{files2Run}.....')

        # ====== calling external APIs
        try:
            external_info = run_all_external_apis(id, ext_dir)
        except Exception as e:
            print(f'Error calling external APIs for company {id} with error: {e}')
            cleanup_vllm()

        # ====== run the LLM the first iteration to clean the info
        try:    
            # ====== get the prompt 
            prompt = make_external_prompt(external_info)
        
            # ====== send the prompt and get the response 
            output_external = send_prompt_vllm(llm, sampling_params, prompt)
        except Exception as e:
            print(f'Error sending the inital prompt for company {id} with error: {e}')
            cleanup_vllm()

        # ====== run the LLM
        
        try:    
            # ====== get the prompt 
            prompt = make_prompt(contextText, output_external, prmpt_settings)
        
            # ====== send the prompt and get the response 
            #output = get_response(tokenizer,model,prompt)
            # using vllm 
            output = send_prompt_vllm(llm,sampling_params,prompt)
            #output = get_response_vllm(output)
        except Exception as e:
            print(f'Error processing the prompt: {e}')
            #print(prompt)
            #output = -1 
            cleanup_vllm()
            #print("Restarting vLLM...")
            #[llm,sampling_params] = set_model_vllm()
            
        
        # cleanup the GPU and CPU every 50 runs 
        if (i) % 50 ==0:
            cleanup_vllm()
            # restart the model 
            print("Waiting for 5 seconds to ensure all processes exit...")
            time.sleep(5)  # Let the system fully release resource
            #print("Restarting vLLM...")
            #[llm,sampling_params] = set_model_vllm()
        # ====== Check the data
            
        if type(output)==str:# data has been extracted 
            
            # ====== transform to JSON and save 
            flagSave = output2json(output,out_dir,err_dir,id,prmpt_settings)

            if flagSave: # file has been succesfully saved 
                print(f'file  {i+1}/{files2Run} processed :)')
                nSaved+=1

            else: # file has not been saved 
                 print(f'file  {i+1} with ID {id} has not been saved :(')
            # if output ==-1 problem in the data extraction 

        else:# data has not been extracted
            print(f'file  {i+1} with ID {id} has not been processed :(') 
    
    # ====== print how many files have been saved 
    print(f'  {nSaved} / {files2Run} have been saved') 
    # finish the process 
    if dist.is_initialized():
        dist.destroy_process_group()
    # print the fields that have be extracted in the last file 
    if (i+1)==files2Run: 
        reqst_fields= get_fields(prmpt_settings)
        print(f"extracted the fields: {" ".join(reqst_fields)}")
        
        
def cleanup_vllm():
    """   Script to clean the GPU and CPU usage """
    print("Cleaning up resources .....")
    
    # step 0: shut down the model 
    #destroy_model_parallel()
    #del llm.llm_engine.model_executor
    #del llm
    #import ray 
    #ray.shutdown()
    
    # Step 1 - cuda memory 
    torch.cuda.empty_cache()
    gc.collect()
    # Step 2: Destroy any active distributed process groups (if using multiple GPUs)
    try:
        if dist.is_initialized():
            dist.destroy_process_group()
            print("Destroyed distributed process group")
    except Exception as e:
        print(f'Error destroying process group: {e}')
    
    # Step 3: Kill any lingering vLLM processes
    current_pid = os.getpid()
    for proc in psutil.process_iter(attrs=['pid', 'name', 'cmdline']):
        try:
            if "vllm" in " ".join(proc.info['cmdline'] or []):
                if proc.info['pid'] != current_pid:  # Don't kill the current script
                    os.kill(proc.info['pid'], signal.SIGKILL)
                    print(f"Killed process: {proc.info['pid']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    print("Cleanup complete!\n")
    
def set_model_vllm():
    # ====== About the model
    model_path = '/home/naic-user/Llama-3.2-3B-Instruct'
    temperature=0.1
    #max_tokens=65536
    max_tokens=10000
    max_model_len = 56688 #65536
    llm = LLM(model=model_path,max_model_len=max_model_len, gpu_memory_utilization=0.75,enable_chunked_prefill=False) # , gpu_memory_utilization=0.8,tensor_parallel_size=2,pipeline_parallel_size=2, 
    sampling_params = SamplingParams(temperature=temperature,max_tokens = max_tokens)
    return [llm,sampling_params]

def send_prompt_vllm(llm, sampling_params, prompt):
    # ====== start the time
    start_time = time.time()
    output = llm.generate([prompt], sampling_params)
    # ====== end time 
    end_time = time.time() - start_time
    print(f"time to process 1 file: {end_time}s")
    try:
        generated_text = output[0].outputs[0].text 
    except:
        generated_text = -1
    return generated_text #generated_text
    
def get_response_vllm(response: requests.Response):
    # function to extract the response of the model

    data = json.loads(response.content)
    try: # check if the response has been created 
        output = data['choices']
        output = output[0]['text']
    except:
        output = -1
    return output    

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
    
    
    
    return generated_text