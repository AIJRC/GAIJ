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

import requests
import time
import json
from typing import List
from documents.document_manager import readfile,save_json
from processing.response_parser import output2json
from vllm import LLM, SamplingParams
import torch
import torch.distributed as dist
import gc
import os 
import psutil
from prompts.prompts_redFlags_unified import prompt_RF,prompt_RF_v2,prompt_wordsContext
import copy 
from vllm.inputs import TextPrompt
import re 

def files_loop(files_list,input_dir,out_dir,nFiles_r):
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
    [llm,sampling_params] = set_model_vllm()
    for i in range(files2Run):
        
        input_file = files_list[i]
        
        # ====== Get the identity of the markdown file 
        input_sep = input_file.split('/')
        id = input_sep[-1][:-3]
        
        # ====== Open the file and read it 
        contextText = readfile(input_dir,input_file)
            
        print(f'extracting data of file  {i+1}/{files2Run}.....') 
        bigJson = None 
        #try:    

            # get the prompt and make it into a message 
        user_prompt,system_prompt = prompt_RF_v2()
        prompt_message = get_message(user_prompt,system_prompt,contextText)
            #print("prompt ready")
            # ====== send the prompt and get the response 
        bigJson = mainProcess(llm,sampling_params,prompt_message,user_prompt,out_dir,bigJson)
            
            # check if there are words of interest in the records 
        foundWords = find_words(contextText)
        if len(foundWords)>0:
                # flagged words 
                print("extracting flagged words")
                #print(f"found words {foundWords}")
                # make the approproate prompt 
                user_prompt,system_prompt = prompt_wordsContext(foundWords)
                prompt_message = get_message(user_prompt,system_prompt,contextText)
                bigJson = mainProcess(llm,sampling_params,prompt_message,user_prompt,out_dir,bigJson)
        #except Exception as e:
            #print(f'Error processing the file: {e}')
            #cleanup_vllm()
               
        
        # ====== save the data 
        if isinstance(bigJson, dict):# data has been extracted 
            
            # ====== transform to JSON and save 
            flagSave = save_json(bigJson,out_dir,id)

            if flagSave: # file has been succesfully saved 
                print(f"file  {i+1}/{files2Run} processed :)") 
                nSaved+=1

            else: # file has not been saved 
                 print(f"file  {i+1} with ID {id} has not been saved :(")
            # if output ==-1 problem in the data extraction 

        else:# data has not been extracted
            print(f"file  {i+1} with ID {id} has not been processed :(") 
        
        # cleanup the GPU and CPU every 50 runs 
        if (i) % 50 ==0:
            cleanup_vllm()
            # restart the model 
            print("Waiting for 5 seconds to ensure all processes exit...")
            time.sleep(5)  # Let the system fully release resource
            #print("Restarting vLLM...")
            #[llm,sampling_params] = set_model_vllm()
    
    # ====== print how many files have been saved 
    print(f"  {nSaved} / {files2Run} have been saved") 
    # finish the process 
    if dist.is_initialized():
        dist.destroy_process_group()
        
        
def mainProcess(llm,sampling_params,prompt_message,user_prompt,out_dir,bigJson):
    " script to run the main process after creating the prompt "
    
    # ==== send prompt 
    response = send_prompt_vllm(llm,sampling_params,prompt_message)
        
    # ====== get the response 
    output = get_response_vllm(response)
    print(output)
    if type(output)==str:
           # ====== transform to JSON and save and (translate )
            [json_data,inference] = output2json(output,out_dir,user_prompt)
            if json_data is not None: 
                # ==== translate the data 
                #json_dataENG = translate_json(json_data)
                json_dataENG = copy.copy(json_data)
                # === save the data 
                if isinstance(json_dataENG, dict):
                    print("adding the extracted data of the file")
                    if bigJson is not None: 
                        bigJson.update(json_dataENG)
                    else: 
                        bigJson = json_data 
                
            flagSaved = 1 
    else:
            flagSaved = 0
    return bigJson 
    


def get_message(user_prompt,system_prompt,context):
    messages = [{"role": "system",
                 "content": system_prompt
                 }, #   # prompt_system
                {"role": "user",
                 "content": user_prompt + context
                 }] # 
    
    #messages = system_prompt  + user_prompt + context + afterContext
   
    return messages

def send_prompt_vllm(llm,sampling_params,message):
    # ====== start the time
    start_time = time.time()
    #output = llm.generate(message,sampling_params=sampling_params)
    output = llm.chat(message,sampling_params=sampling_params)
    # ====== end time 
    end_time = time.time() - start_time
    print(f"time to process 1 file: {end_time}s")
    #try:
    #    generated_text = output[0].outputs[0].text 
    #except:
    #    generated_text = -1
    return output #generated_text #generated_text
    
def get_response_vllm(genText):

    # function to extract the response of the model

    #data = json.loads(response.content)
    
   
    try:
        #output = genText['choices'][0]['message']['content']
        #output = output[0]['text']
        #output = data[0]['choices']#['content']
        output = genText[0].outputs[0].text.strip()
    except:
        output = -1
    return output

def set_model_vllm():
    # ====== About the model
    model_path = 'deepseek-ai/DeepSeek-R1-Distill-Llama-8B'
    temperature=0.0
    max_tokens=2000 # 2000
    max_model_len = 8192#4096#8192# 45472#56688
    #llm = LLM(model=model_path, max_model_len=max_model_len,gpu_memory_utilization=0.65,enable_chunked_prefill=False,tensor_parallel_size=2,pipeline_parallel_size=2) # , gpu_memory_utilization=0.8,tensor_parallel_size=2,pipeline_parallel_size=2, 
    llm = LLM(model=model_path, max_model_len=max_model_len,gpu_memory_utilization=0.6,enable_chunked_prefill=True,tensor_parallel_size=2,pipeline_parallel_size=1) # , gpu_memory_utilization=0.8,tensor_parallel_size=2,pipeline_parallel_size=2, 

    sampling_params = SamplingParams(temperature=temperature,max_tokens = max_tokens)
    return [llm,sampling_params]

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
        print(f"Error destroying process group: {e}")
    # test this: 
    os.system("pkill -f vllm")
    del llm
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

def find_words(text):
    " use regex to find particular words in the tax record"
    words2find = ["kompensasjon", "sluttavtale", "oppsigelsesdato", "oppsigelse", "sluttdato", "opphør", "trukket", "etterlønn", "bonus", "variabel lønn", "resultatbasert", "milepæl", "etterbetaling", "etterbetalt", "privatlån", "private lån", "selgerkreditt", "interntransaksjon", "diskresjonær", "låneforfall", "forfalt", "ubetalt", "solgt aksjer"]
    people2find = ["Kjell Inge Røkke"]
    # concatenate all the words
    allwords2find = words2find + people2find
    # Compile a regex pattern to match unwanted words
    #pattern_words = r"\b(" + "|".join(allwords2find) + r")\b"        
    #foundWords = [word for word in allwords2find if re.search(r"\b(" + "|".join(word) + r")\b",text, flags=re.IGNORECASE)]
    foundWords = [word for word in allwords2find if re.search(rf'\b{re.escape(word)}s?\b',text, flags=re.IGNORECASE)]

    return foundWords  