"""
Prompt template in ENG and NOR 
    """
import copy 

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
    The name of the company can not be: Brønnøysund.
    The address of the company can not be: postboks 900, 8910.
    You should extract information about the company, not the tax office
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
