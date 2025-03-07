"""
Created on Tue Dec 10 2024

"""

# =========================================================================
"""
Goal: Clean the output in a JSON format from the LLM to store it in a standardized form
"""
# =========================================================================
import sys
import re
import warnings
import copy
import json
import pandas as pd
import os
from datetime import datetime
from utils.support_functions import fieldNames_dict, get_fields, is_number,is_percentage
from documents.document_manager import save_JSON,save_text
from test.test_scripts import check_words
from prompts.prompt_manager import get_prompt


def output2json(output,out_dir,err_dir,id,prmpt_settings):
    """ function to transform the output of the model into a json format and save it in a
    standardized form 
       if the format is not right save it as an error file, 
       or a NA file if the file is missing all together """
    
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
            
            # add version control 
            cleaned_JSON_ver = add_versioncontrol(cleanded_JSON,prmpt_settings)

            # Save the JSON data to a file
            flagSave = save_JSON(cleaned_JSON_ver,json_path2save)
           
        
        except json.JSONDecodeError as e: # Error in the spelling
            print(f"Error decoding JSON: {e}")
            # save the id of the file in the error folder 
            errFile = 'er_' + id +'.txt'
            # save ID to error file 
            flagSave = save_text(os.path.join(err_dir,errFile),str(id))
            
    else: # the output did not procude a file 
        print("No JSON found in the response")
        NAFile = 'na_' + id +'.txt'
        # save ID to N/A file 
        flagSave = save_text(os.path.join(err_dir,NAFile),str(id))
    
    return flagSave

def get_standardStructure(json_data,prmpt_settings):
    " script to standarize the output of the LLM "
    data_new = dict()
    # get the list of the requested fields 
    reqst_fields = get_fields(prmpt_settings)
    # Get the language of the prompt 
    if prmpt_settings.NOR_Flag:
        lng ='NOR'
    else:
        lng = 'ENG'
    
    for field in reqst_fields:
       
        # extract the data for that file 
        extData = get_extractedData(field,lng,json_data)
        # check if the entry is invalid - different types of empty
        dataChecked = check_empty(extData)
            # clean the data if the field is not empty
        if (not dataChecked)==False:
            # check if the field name is organization type ( if so special tratment)
            if field =='type':
                dataChecked = check_org_type(dataChecked) 
            # Clean the data 
            cleaned_data = cleanData(dataChecked)
            
            if field =='address':
                try:
                    cleaned_data =[", ".join(cleaned_data)]
                except TypeError:
                    cleaned_data = [copy.copy(cleaned_data)]
            data2save = copy.copy(cleaned_data)
        else:
            data2save = copy.copy(dataChecked)
        
        # check for the unwanted words 
        #check_words(field,data2save)
        
        # formmating the words - only capitalize the first letter except if it is AS
        if data2save is not None: 
            data2save = format_input(data2save)
        
        # add it to the new JSON structure 
        if field == 'leadership':
            # get  all the field names and their translations 
            dataFields_dict = fieldNames_dict()
            # Get the name in the JSON file
            fieldName = dataFields_dict[field][lng]
            data_new[field] = {"names":data2save,"roles":json_data[fieldName]}
        else:
            data_new[field] = data2save
        
        
    return data_new

def get_extractedData(field,lng,json_data):
    " script to extract data from a field of the JSON file "
    
    extData =[]
    
    # get  all the field names and their translations 
    dataFields_dict = fieldNames_dict()
    # Get the name in the JSON file
    fieldName = dataFields_dict[field][lng]
    # find if the field is present in the JSON file 
    if fieldName in json_data:
        # check if the field name is leadership ( if so special treatment)
        if (fieldName =='leadership') | (fieldName == 'Lederskap'):
            # this is a nested dictionary extract all the info as a single list 
            
            for sfield in json_data[fieldName]:
                try:
                    tempData = sfield['name']
                    # check if its a list 
                    if isinstance(tempData,list):
                        extData.extend(tempData)
                    else:
                        extData.append(tempData)
                except KeyError:
                    tempData =[]

            # also remove any numbers 
            try:
                extData = [item for item in extData if not is_number(item)]
            except TypeError:
                extData = []
            if extData is not None and extData:
                # and percentages 
                extData = [item for item in extData if not is_percentage(item)]
       
        
        else: # any other field - no nested dictionary 
            # get the extracted data 
            extData = json_data[fieldName]
    else:
        # there is no data to extract 
        print(f"No data extracted for {field}")
    
    return extData

def check_empty(extData):
    " ======= Function to check if the data extracted is empty "
        # list of possible empty options provided by the LLM 
    empty_options= ['null',"none",'nan','string','string or null','integer or null','boolean or null','n/a','none','no data available',"","unknown","---","nei"]
        # check if the extracted data matches any of these 
    # the extracted data is a list 
    if  isinstance(extData,list):
        if len(extData)==0:
            data_return = None
        else:
            # remove actually empty data 
            extData = [data for data in extData if ((not data)==False)]
            remove_fields = [dat for dat in extData if dat.lower() in empty_options]
            if not remove_fields: # no empty fields 
                data_return = copy.copy(extData)
            else:  # if any has a value
                data_return = list(set(extData) - set(remove_fields))
            if len(data_return)==0:
                data_return = None
    elif extData is None:
        data_return = None
    else: # only one element
        # check if it is empty
        if extData.lower() in empty_options: 
            data_return = None
        else: 
            data_return = copy.copy(extData)
    return data_return
        
        
def cleaningProtocol(data2clean):
    " script with a protocol to clean a data item"
    # pattern of unwanted symbols 
    pattern = r"(^-?\d+(\.\d+)?([,\s%-]-?\d+(\.\d+)?)*\s*%?\s*\n)"
    # unwanted words 
    unwanted_words =["brønnøysundregistrene","lederskap","styremedlemmer","ledende","leder","daglig leder","styrets leder","ledelsen","styreleder","styremedlem","lenn","100.0%","styret"," eierandel","stemmeandel"," direkte og indirekte","100%"]
    # Compile a regex pattern to match unwanted words
    pattern_words = r"\b(" + "|".join(unwanted_words) + r")\b"
    
    # Remove content within brackets (both [] and ())
    nobrack_item = re.sub(r"\(.*?\)|\[.*?\]", "", data2clean)
    # remove unwanted symbols and spaces 
    cleaned_data_2 = "".join([re.sub(pattern, "", string) for string in nobrack_item])
    # Remove unwanted words
    cleaned_data_1 = re.sub(pattern_words, "", cleaned_data_2, flags=re.IGNORECASE)
    # separate the commas 
    cleaned_data = [s.strip() for s in cleaned_data_1.split(",")]
    # remove single words
    cleaned_data =[s for s in cleaned_data if len(s.split(" "))>1]
   
    return cleaned_data
    
def cleanData(data2Clean):
    """ script to clean the data ( get the unique values and sort them alphabetically + 
    remove unwanted items ) """
    # Clean the data 
    # if it is a list 
    if isinstance(data2Clean,list): 
        cleanData =[]
        for item in data2Clean:
                cleanData.extend(cleaningProtocol(item))
        # remove empty spaces 
        cleanData = list(filter(None, cleanData))
        # sort it and get the unique values        
        cleaned_data = sorted(set(cleanData))

    else:
        cleaned_data = cleaningProtocol(data2Clean)
        cleaned_data = check_empty(cleaned_data)
    
    return cleaned_data

def check_org_type(type_data):
    
    """ script to check wether the extracted organization type matches the official ones """
    # get the list of organizations 
    orgTypesFile = os.path.join(os.path.dirname(__file__), "types_of_organisation.xlsx")
    df_oT = pd.read_excel(orgTypesFile)
        # check if the type_data is in among the organizatio types 
    matches_oT = df_oT.isin([type_data])
        # get the field in english
    lang = "english"
    if matches_oT.any().any():
        # Get row and column indices
        row_index = matches_oT.idxmax(axis=0).loc[matches_oT.any(axis=0)], matches_oT.idxmax(axis=1).loc[matches_oT.any(axis=1)]
        # get the name of the organization in english ( in case this was not the case)
        name_org = df_oT.loc[row_index[0].iloc[0],lang]
    else: 
        name_org = "not recogized"
    return name_org

            
            
def formatting_string(text):
    words = text.split()
    
    formatted_words = [
        word.upper() if word.upper() == "AS" else word.capitalize()
        for word in words
    ]
    joinedWords = " ".join(formatted_words)
    return joinedWords

def format_input(input):
    try:
        if len(input)>1:
            formatted_text = []
            for item in input:
                formatted_temp = formatting_string(item)
                formatted_text.append(formatted_temp)
        else:
            formatted_text = formatting_string(input[0])
    except: 
        formatted_text = input
    return formatted_text

def add_versioncontrol(cleanded_JSON,prmpt_settings):
    " add the version control to the JSON "
    # get the values
    curr_version = 'v1_Llama_3.2_3B'
    date = datetime.today().strftime('%Y-%m-%d')
    prompt_LANG = "ENG"
    if prmpt_settings.NOR_Flag:
        prompt_LANG = "NOR"
    prompt = get_prompt(prmpt_settings)
    # make it into a dictionary
    version_control = dict()
    version_control = {"version_control":{"version":curr_version,"date":date,"prompt_lang":prompt_LANG,"prompt":prompt}}
    # update the JSON 
    cleanded_JSON.update(version_control)
    
    return cleanded_JSON

            
            

    
    
        
        
    
      
        
        