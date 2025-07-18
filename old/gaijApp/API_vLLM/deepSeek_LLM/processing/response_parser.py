"""
Created on Tue Dec 10 2024

"""

# =========================================================================
"""
Goal: Clean the output in a JSON format from the LLM to store it in a standardized form
"""
# =========================================================================
import re
import copy
import json
import os
from datetime import datetime
import deepl 


def output2json(output,out_dir,user_prompt):
    print(f"geting the output of the data")
    # function to transform the output of the model into a json format and save it 
    #  Sepparate the inference from the JSON formatted output 
    
    splt_output = output.split('</think>',1)
    
    inference = copy.copy(splt_output[0])
    # ======== Use regex to extract the JSON block from the response
    json_str_match = re.search(r'{.*}', splt_output[1], re.DOTALL)
    json_path = out_dir
    if not os.path.isdir(json_path):
        os.mkdir(json_path)
    
    if json_str_match:
        json_str = json_str_match.group(0)
        
        # === Parse the JSON string
        try:
            # get the JSON data
            json_data = json.loads(json_str)

	    # add version control 
            json_data = add_versioncontrol(json_data,user_prompt)
            
        
        # ==== Error in the spelling
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            json_data = [] 
            
    else:
        # ==== the output did not procude a file 
        print("No JSON found in the response")
        json_data = []
    
    return [json_data,inference]

def translate_json(json_data):
    " script to translate the output of the LLM using deepL "
    auth_key = "7b4bf51e-3423-4140-8d80-c9ccdfbbfda1:fx"
    deepl_client = deepl.DeepLClient(auth_key)
    
    #print(json_data)
    # loop though all the notes
    #print(type(json_data["notes"]))
    #print(type(json_data["footnotes"]))
    try:
        # translate the notes 
        for note in json_data["notes"]:
            #print(note)
            #data2tranlate = note["summary"]
            # translate the summary: 
            data2tranlate = note.get("summary")
            dataTranslated = deepl_client.translate_text(data2tranlate, target_lang='EN-US')
            # update the dictionary 
            note.update({"summary":dataTranslated.text})
            # translate the title: 
            data2tranlate = note.get("title")
            dataTranslated = deepl_client.translate_text(data2tranlate, target_lang='EN-US')
            # update the dictionary 
            note.update({"title":dataTranslated.text})
            
        # translate the footnotes
        for footnote in json_data["footnotes"]:
            #print(footnote)
            #data2tranlate = footnote["summary"]
            data2tranlate = footnote.get("summary")
            dataTranslated = deepl_client.translate_text(data2tranlate, target_lang='EN-US')
            # update the dictionary 
            footnote.update({"summary":dataTranslated.text})
    except TypeError:
        #print(json_data)
        a = 1 
    
    return json_data
    
def add_versioncontrol(cleanded_JSON,user_prompt):
    " add the version control to the JSON "
    # get the values
    curr_version = 'v1_deepSeek_R1-Distill-Llama-8B'
    date = datetime.today().strftime('%Y-%m-%d')
    
    # make it into a dictionary
    version_control = dict()
    version_control = {"version_control":{"version":curr_version,"date":date,"prompt":user_prompt}}
    # update the JSON 
    cleanded_JSON.update(version_control)
    
    return cleanded_JSON

            
            

    
    
        
        
    
      
        
        