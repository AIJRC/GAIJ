"""
Created on Tue Dec 10 2024

"""

# =========================================================================
"""
Goal: Clean the output in a JSON format from the LLM to store it in a standardized form
"""
# =========================================================================
import re
import warnings
import copy
import pandas as pd
from prompt_API import fieldNames_dict,get_fields


def get_extractedData(field,lng,json_data):
    # ==== Function to extract data from a field of the JSON file 
    
    extData =[]
    
    # get  all the field names and their translations 
    dataFields_dict = fieldNames_dict()
    # Get the name in the JSON file
    fieldName = dataFields_dict[field][lng]
    # find if the field is present in the JSON file 
    if fieldName in json_data:
        
        # check if the field name is leadership ( if so special treatment)
        if field =='leadership':
            # this is a nested dictionary extract all the info as a single list 
            
            for sfield in json_data[fieldName]:
                tempData = json_data[fieldName][sfield]
                # check if its a list 
                if isinstance(tempData,list):
                    extData.extend(tempData)
                else:
                    extData.append(tempData)
            
            # also remove any numbers 
            extData = [item for item in extData if not is_number(item)]
    
        else: # any other field - no nested dictionary 
            # get the extracted data 
            extData = json_data[fieldName]
    else:
        # there is no data to extract 
        warnings(f"No data extracted for '{field}'")
    
    return extData

def check_empty(extData):
    # ======= Function to check if the data extracted is empty 
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
        
    
def cleanData(data2Clean):
    # function to clean the data ( get the unique values and sort them alphabetically + 
    # remove unwanted items )
    # Clean the data 
        # unwanted symbols and spaces 
    pattern = r"(^-?\d+(\.\d+)?([,\s%-]-?\d+(\.\d+)?)*\s*%?\s*\n)"
    # step 1: get only uniqe entries and sort it alphabetically - if it's a list  
    if isinstance(data2Clean,list): 
        if len(data2Clean)>1:
            data2Clean = sorted(set(data2Clean))
    # step 2: remove unwanted symbols and spaces 
            cleaned_data = [re.sub(pattern, "", string) for string in data2Clean]
        else:
            cleaned_data = "".join([re.sub(pattern, "", string) for string in data2Clean])
    else:
        cleaned_data = "".join([re.sub(pattern, "", string) for string in data2Clean])
    
    return cleaned_data

def check_org_type(cleaned_data):
    
    # function to check wether the extracted organization type matches the official ones 
        # get the list of organizations 
    orgTypesFile = "types_of_organisation.xlsx"
    df_oT = pd.read_excel(orgTypesFile)
        # check if the cleaned_data is in among the organizatio types 
    matches_oT = df_oT.isin([cleaned_data])
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

def is_number(item):
    if (not item)==False:
        try:
            float(item)  # Attempt to convert to a float
            return True
        except ValueError:
            return False
    else:
        return False
            
            
def get_standardStructure(json_data,prmpt_settings):
    
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
            # Clean the data 
            cleaned_data = cleanData(dataChecked)
            # check if the field name is organization type ( if so special tratment)
            if field =='type':
                cleaned_data = check_org_type(cleaned_data)
            data2save = copy.copy(cleaned_data)
        else:
            data2save = copy.copy(dataChecked)
        
        # add it to the new JSON structure 
        data_new[field] = data2save
        
    return data_new
    
    
        
        
    
      
        
        