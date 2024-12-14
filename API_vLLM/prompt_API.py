"""
Created on Tue Dec 10 2024

"""

# =========================================================================
"""
Goal: Provide a prompt that will be used to run the API 
    This is part of the API pilepile 
    
    Abreviations of the fields:
        Company name: name
        Company ID: id
        Company address: adrs
        Company type: typ
        Leadership: lead
        Subsidiaries: subs
        Parent company: parnt 
    
    
"""
# =========================================================================
import argparse
import copy


# ======= Make the prompt 
def mk_prompt(prmpt_settings):
    # Get the right prompt 
    if prmpt_settings.NOR_Flag:
        print(f"the prompt is in Norwegian")
        prompt_quest=prompt_NOR(prmpt_settings)
    else:
        prompt_quest=prompt_ENG(prmpt_settings)
   
    return prompt_quest


# ====== Prompt question English 
def prompt_ENG(prmpt_settings):

    prompt_quest_temp = """
    <|system|> You are a helpful assistant. You process tax records of Norwegian companies and extract specific information from them, then present it in a structured JSON format. 
    This is the tax record you will base your answers on: {content}

    Please return only the response in the following JSON format. Do not include any explanation, comments, or extra information.

    The JSON structure should strictly follow this format:

    {
        """ 
    if prmpt_settings.name_Flag:
        prompt_quest_temp = prompt_quest_temp + """ 
        "company_name": "string", """
    if prmpt_settings.id_Flag:
        prompt_quest_temp = prompt_quest_temp + """      
        "company_id": "string","""
    if prmpt_settings.adrs_Flag:
        prompt_quest_temp = prompt_quest_temp + """    
        "company_address": "string", """
    if prmpt_settings.typ_Flag:
        prompt_quest_temp = prompt_quest_temp + """ 
        "company_type": "string","""
    if prmpt_settings.lead_Flag:
            prompt_quest_temp = prompt_quest_temp + """ 
        "leadership": {
            "CEO": "string or null",       
            "board_members": [
                "string" or null           
            ],
             "share_holders": [
                "string" or null           
            ],
            "chairman_of_the_board": "string or null" 
        },"""
    if prmpt_settings.subs_Flag:
        prompt_quest_temp = prompt_quest_temp + """ 
        "subsidiaries": [
            "string" or null               
        ], """
    if prmpt_settings.parnt_Flag:
        prompt_quest_temp = prompt_quest_temp + """ 
        "parent_company": "string or null","""
       
    prompt_quest_temp2 = prompt_quest_temp.rstrip(',') + """
    }
    
    <|user|> Please extract the following information from the tax record:
    """
    if prmpt_settings.name_Flag:
        prompt_quest_temp2 = prompt_quest_temp2 +"""
        - "company_name": The name of the company.
        """
    if prmpt_settings.id_Flag:
        prompt_quest_temp2 = prompt_quest_temp2 +"""
        - "company_id": The company tax number.
        """
    if prmpt_settings.adrs_Flag:
        prompt_quest_temp2 = prompt_quest_temp2 +"""
        - "company_address": The company's address.
        """
    if prmpt_settings.typ_Flag:
        prompt_quest_temp2 = prompt_quest_temp2 +"""
        - "company_type": The type of the company as specified on the first page of the tax record.
        """
    if prmpt_settings.lead_Flag:
        prompt_quest_temp2 = prompt_quest_temp2 +"""
        - "leadership": This is a nested dictionary with the following information:
            - "CEO": Name of the CEO.
            - "board_members": List of board members (if available).
            - "share_holders": List of share holders (if available).
            - "chairman_of_the_board": Name of the chairman of the board of the company.
        """
    if prmpt_settings.subs_Flag:
        prompt_quest_temp2 = prompt_quest_temp2 +"""    
        - "subsidiaries": List of the subsidiaries of the company (empty list if none).
        """
    if prmpt_settings.parnt_Flag:
        prompt_quest_temp2 = prompt_quest_temp2 +"""
        - "parent_company": Name of the parent company (null if not available).
        """
    
    
    prompt_quest_temp2 = prompt_quest_temp2 +"""
    Please ensure that all fields are included, even if they are empty or null.
    Only return the JSON response; do not add explanations, comments, or repeated entries.
    <|assistant|>
    """
    prompt_quest = copy.copy(prompt_quest_temp2)
    return prompt_quest
# ====================== Prompt Question Norwegian 
def prompt_NOR(prmpt_settings):
    prompt_quest_temp = """
   <|system|> Du er en hjelpsom assistent. Du behandler norske selskapers skattelister og trekker ut spesifikk informasjon fra dem, og presenterer den i et strukturert JSON-format. 
    Dette er skatteoppføringen du vil basere svarene dine på: {context}

    Vennligst returner kun svaret i følgende JSON-format. Ikke ta med forklaringer, kommentarer eller ekstra informasjon.

    JSON-strukturen skal strengt følge dette formatet:

    {
        """ 
    if prmpt_settings.name_Flag:
        prompt_quest_temp = prompt_quest_temp + """ 
        "Foretaksnavn": "string", """
    if prmpt_settings.id_Flag:
        prompt_quest_temp = prompt_quest_temp + """      
        "Organisasjonsnummer": "string","""
    if prmpt_settings.adrs_Flag:
        prompt_quest_temp = prompt_quest_temp + """    
        "Forretningsadresse": "string", """
    if prmpt_settings.typ_Flag:
        prompt_quest_temp = prompt_quest_temp + """ 
        "Organisasjonsform": "string","""
    if prmpt_settings.lead_Flag:
            prompt_quest_temp = prompt_quest_temp + """ 
        "Lederskap": {
            "Representant_for_selskapet": "string or null",       
            "Styremedlemmer": [
                "string" or null           
            ],
             "Aksjeeiere": [
                "string" or null           
            ],
            "Styreleder": "string or null" 
        },"""
    if prmpt_settings.subs_Flag:
        prompt_quest_temp = prompt_quest_temp + """ 
        "Datterselskaper": [
            "string" or null               
        ], """
    if prmpt_settings.parnt_Flag:
        prompt_quest_temp = prompt_quest_temp + """ 
        "Morselskap": "string or null","""
       
    prompt_quest_temp2 = prompt_quest_temp.rstrip(',') + """
    }
    
    <|user|> Vennligst hent ut følgende informasjon fra skatteoppføringen:
    """
    if prmpt_settings.name_Flag:
        prompt_quest_temp2 = prompt_quest_temp2 +"""
        - Foretaksnavn: Navnet på selskapet.
        """
    if prmpt_settings.id_Flag:
        prompt_quest_temp2 = prompt_quest_temp2 +"""
        - Organisasjonsnummer: Selskapets skattenummer.
        """
    if prmpt_settings.adrs_Flag:
        prompt_quest_temp2 = prompt_quest_temp2 +"""
        - Forretningsadresse: Selskapets adresse.
        """
    if prmpt_settings.typ_Flag:
        prompt_quest_temp2 = prompt_quest_temp2 +"""
        - Organisasjonsform: Selskapstypen som er spesifisert på første side i skatteregistreringen.
        """
    if prmpt_settings.lead_Flag:
        prompt_quest_temp2 = prompt_quest_temp2 +"""
        - Lederskap: Dette er en nøstet ordbok med følgende informasjon:
            - "Representant_for_selskapet": Navnet på administrerende direktør.
            - Styremedlemmer: Liste over styremedlemmer (hvis tilgjengelig).
            - Aksjeeiere: Liste over aksjeeiere: Liste over aksjeeiere (hvis tilgjengelig).
            - Styreleder: Navnet på selskapets styreleder.
        """
    if prmpt_settings.subs_Flag:
        prompt_quest_temp2 = prompt_quest_temp2 +"""    
        - Datterselskaper: Liste over datterselskaper: Liste over selskapets datterselskaper (tom liste hvis ingen).
        """
    if prmpt_settings.parnt_Flag:
        prompt_quest_temp2 = prompt_quest_temp2 +"""
        - Morselskap: Navn på morselskapet (null hvis ikke tilgjengelig).
        """
    
    
    prompt_quest_temp2 = prompt_quest_temp2 +"""
    Please ensure that all fields are included, even if they are empty or null.
    Only return the JSON response; do not add explanations, comments, or repeated entries.
    <|assistant|>
    """
    prompt_quest = copy.copy(prompt_quest_temp2)
    return prompt_quest

# ==== support functions: 
# ====  dictionary with all the field names ( standar , in english and in Norwegian)
def fieldNames_dict():
    fields_NOR = ["Foretaksnavn", "Organisasjonsnummer","Forretningsadresse","Organisasjonsform","Lederskap","Datterselskaper","Morselskap"]
    fields_ENG = ["company_name","company_id","company_address","company_type","leadership","subsidiaries","parent_company"]
    fields_general = ["name","ID","address","type","leadership","subsidiaries","parent"]
    dataFields_dict = dict()
    for i in range(len(fields_general)):
        field = fields_general[i]
        dataFields_dict[field] = dict()
        dataFields_dict[field]['NOR'] = fields_NOR[i]
        dataFields_dict[field]['ENG'] = fields_ENG[i]
    
    return dataFields_dict

# === list of the fields requested to be extracted   
def get_fields(prmpt_settings):
    # function to get a list of all he requested fields in the prompt 
    reqst_fields = []
        # Name
    if prmpt_settings.name_Flag == True:
        reqst_fields.append('name')
         # ID
    if prmpt_settings.id_Flag == True:
        reqst_fields.append('ID')
        # Address
    if prmpt_settings.adrs_Flag == True:
        reqst_fields.append('address')
        # Type of company
    if prmpt_settings.typ_Flag == True:
        reqst_fields.append('type')
        # Leadership of the company
    if prmpt_settings.lead_Flag == True:
        reqst_fields.append('leadership')
        # Subsidiaries
    if prmpt_settings.subs_Flag == True:
        reqst_fields.append('subsidiaries')
        # Parent Company
    if prmpt_settings.parnt_Flag == True:
        reqst_fields.append('parent')
    
    return reqst_fields
# === dictionary that allows for dot structure  
class DotDict(dict):
    """A dictionary that supports dot notation."""
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        del self[key]
# ==========================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='prompt selection for LLMM')
    parser.add_argument('--NOR_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask for the prompt to be in Norwegian - default FALSE')
    parser.add_argument('--AllFields_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask to select all the information files of the prompt - default TRUE')
    parser.add_argument('--name_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask to extract the Name of the company - default TRUE only available if AllFields_Flag==FALSE')
    parser.add_argument('--id_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask to extract the ID of the company - default TRUE only available if AllFields_Flag==FALSE')
    parser.add_argument('--adrs_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask to extract the Address of the company - default TRUE only available if AllFields_Flag==FALSE')
    parser.add_argument('--typ_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask to extract the Type of company - default TRUE only available if AllFields_Flag==FALSE')
    parser.add_argument('--lead_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask to extract the Leadership of the company - default TRUE only available if AllFields_Flag==FALSE')
    parser.add_argument('--subs_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask to extract the subsidiaries of the company - default TRUE only available if AllFields_Flag==FALSE')
    parser.add_argument('--parnt_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask to extract the Parent company of the company - default TRUE only available if AllFields_Flag==FALSE')
    #parser.add_argument('--id_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask to extract the ID of the company - default TRUE only available if AllFields_Flag==FALSE')
    args = parser.parse_args()
    
    # Create a prompt setting arguments that supports dot notation 
    prmpt_settings = DotDict()    
    
    # ===== get the arguments 
        # ===== get the arguments - prompt settings
    
        # Flag for the prompt to be in NORWEGIAN 
    if args.NOR_Flag is not None:
        prmpt_settings.NOR_Flag = args.NOR_Flag
    else:
        prmpt_settings.NOR_Flag = False
        # Flag to extract all the possible data fields 
    if args.AllFields_Flag is not None:
        prmpt_settings.AllFields_Flag = args.AllFields_Flag  
    else:
        prmpt_settings.AllFields_Flag = True
    
   
    
        # IF only some fields are needed 
    if prmpt_settings.AllFields_Flag == False: 
    
            
            # Flag to extract Name
        if args.name_Flag is not None:
            prmpt_settings.name_Flag = args.name_Flag
        else:
            prmpt_settings.name_Flag = False
        
            # Flag to extract ID
        if args.id_Flag is not None:
            prmpt_settings.id_Flag = args.id_Flag
        else:
            prmpt_settings.id_Flag = False
            # Flag to extract Address
        if args.adrs_Flag is not None:
            prmpt_settings.adrs_Flag = args.adrs_Flag
        else:
            prmpt_settings.adrs_Flag = False
            # Flag to extract Type of company
        if args.typ_Flag is not None:
            prmpt_settings.typ_Flag = args.typ_Flag
        else:
            prmpt_settings.typ_Flag = False
            # Flag to extract Leadership of the company
        if args.lead_Flag is not None:
            prmpt_settings.lead_Flag = args.lead_Flag
        else:
            prmpt_settings.lead_Flag = False
            # Flag to extract Subsidiaries
        if args.subs_Flag is not None:
            prmpt_settings.subs_Flag = args.subs_Flag
        else:
            prmpt_settings.subs_Flag = False
            # Flag to extract Parent Company
        if args.parnt_Flag is not None:
            prmpt_settings.parnt_Flag = args.parnt_Flag
        else:
            prmpt_settings.parnt_Flag = False
        #    # Flag to extract Name
        #if args.name_Flag is not None:
        #    name_Flag = args.name_Flag
        #else:
        #    name_Flag = False
    else: 
        # All of the data fields are true 
        prmpt_settings.name_Flag = True
        prmpt_settings.id_Flag = True
        prmpt_settings.adrs_Flag = True
        prmpt_settings.typ_Flag = True
        prmpt_settings.lead_Flag = True
        prmpt_settings.subs_Flag = True
        prmpt_settings.parnt_Flag= True
        #prmpt_settings.name_Flag = True
    
    #print(prmpt_settings)    
    prompt_question = mk_prompt(prmpt_settings)
    print(prompt_question)
    
    
    
