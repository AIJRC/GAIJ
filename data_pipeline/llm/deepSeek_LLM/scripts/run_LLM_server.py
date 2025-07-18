"""
Created on Tue Dec 10 2024

"""

# =========================================================================
"""
Goal: run the markdonwfiles through an LLM to extract the important information in a JSON formatted
document, the LLM is run in the server
     This is the main component of the pipeline which inculdes
     - Getting the input
     - Selecting the right prompt 
     - Run the LLM
     - Clean the output and save it 

"""
# =========================================================================

import re
import requests
import time
import json
import copy
from typing import List
from prompts.prompts_redFlags_unified import prompt_RF_v2,prompt_wordsContext
from documents.document_manager import readfile,save_json
from processing.response_parser import output2json


def files_loop(files_list,input_dir,out_dir,nFiles_r):
    flag_separatePrompts = False
    # function to loop through the folder with the markdown files (to be processed) and extract 
    # the text from each of them using LLM -- Main function
    
    nFiles = len(files_list)
    if (nFiles_r==-1) | (nFiles<nFiles_r):
        files2Run = nFiles
    else:
        files2Run = nFiles_r
    print(f"{files2Run} files will be processed from {input_dir}")
    for i in range(files2Run):
        
        input_file = files_list[i]
        
        # ====== Get the identity of the markdown file 
        input_sep = input_file.split('/')
        id = input_sep[-1][:-3]
        
        # ====== Open the file and read it 
        contextText = readfile(input_dir,input_file)
            
        print(f'extracting data of file  {i+1}/{files2Run}.....') 
        bigJson = None
        
        
        try:    

            # get the prompt 
            user_prompt,system_prompt = prompt_RF_v2()
            # send the prompt and get the response 
            bigJson = mainProcess(user_prompt,system_prompt,contextText,out_dir,bigJson)
            
            # check if there are words of interest in the records 
            foundWords = find_words(contextText)
            if len(foundWords)>0:
                # flagged words 
                print("extracting flagged words")
                #print(f"found words {foundWords}")
                # make the approproate prompt 
                user_prompt,system_Prompt = prompt_wordsContext(foundWords)
                # send the prompt and get the response 
                bigJson = mainProcess(user_prompt,system_Prompt,contextText,out_dir,bigJson)
        except Exception as e:
            print(f'Error processing the file: {e}')
        
            
       
          
          
        # ===== save the data 
        if isinstance(bigJson, dict):
            save_json(bigJson,out_dir,id)
            print(f"file  {i+1}/{files2Run} processed :)") 
        else:
            print(f"file  {i+1} with ID {id} notes have not been processed :(") 
           
        

def mainProcess(user_prompt,system_prompt,contextText,out_dir,bigJson):
    " script to run the main process after creating the prompt "
    # ==== send prompt 
    response = send_prompt(user_prompt+ contextText ,system_prompt)
        
    # ====== get the response 
    output = get_response(response)
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
                #if isinstance(json_dataENG, dict):
                #    savejson(json_dataENG,out_dir,id)
            #if flag_saveInference:
                #saveInference(inference,out_dir)
            flagSaved = 1 
    else:
            flagSaved = 0
    return bigJson 
              

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
    #"http://localhost:8000/v1/chat/completions",#
    'http://gaijl4slur-g2gpunodeset-0:8000/v1/chat/completions',
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


def find_words(text):
    " use regex to find particular words in the tax record"
    words2find = ["kompensasjon", "sluttavtale", "oppsigelsesdato", "oppsigelse", "sluttdato", "opphør", "trukket", "etterlønn", "bonus", "variabel lønn", "resultatbasert", "milepæl", "etterbetaling", "etterbetalt", "privatlån", "private lån", "selgerkreditt", "interntransaksjon", "diskresjonær", "låneforfall", "forfalt", "ubetalt", "solgt aksjer","covid","covid-19"]
    people2find = ["Kjell Inge Røkke"]
    # concatenate all the words
    allwords2find = words2find + people2find
    # Compile a regex pattern to match unwanted words
    #pattern_words = r"\b(" + "|".join(allwords2find) + r")\b"        
    #foundWords = [word for word in allwords2find if re.search(r"\b(" + "|".join(word) + r")\b",text, flags=re.IGNORECASE)]
    foundWords = [word for word in allwords2find if re.search(rf'\b{re.escape(word)}s?\b',text, flags=re.IGNORECASE)]

    return foundWords  