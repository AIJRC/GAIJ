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

from utils.arg_parser import argparser_prompt,parser_prompt
from prompts.prompt_templates import prompt_ENG,prompt_NOR


# ======= Make the prompt 
def make_prompt(contextText,prmpt_settings):
    " make the prompt: Question + Text "
    # function to create the prompt including the info from the file 

    # ====== Prompt question 
    prompt_question=get_prompt(prmpt_settings)
        # To do: print the fields that are being extracted and the language 
    # ====== Complete the prompt 
    prompt_text = contextText + prompt_question

    return prompt_text


def get_prompt(prmpt_settings):
    " Get the right prompt question"
    if prmpt_settings.NOR_Flag:
        print(f"the prompt is in Norwegian")
        prompt_quest=prompt_NOR(prmpt_settings)
    else:
        prompt_quest=prompt_ENG(prmpt_settings)
   
    return prompt_quest


def check_promptSettings(prmpt_settings):
    " check whether all the fields are present in the settings" 
    if prmpt_settings.AllFields_Flag== False:
            if "name_Flag" not in prmpt_settings:
                prmpt_settings.name_Flag = False
                print('name extraction has been set to False')
            if "id_Flag" not in prmpt_settings:
                prmpt_settings.id_Flag = False
                print('ID extraction has been set to False')
            if "adrs_Flag" not in prmpt_settings:
                prmpt_settings.adrs_Flag = False
                print('address extraction has been set to False')
            if "lead_Flag" not in prmpt_settings:
                prmpt_settings.lead_Flag = False
                print('leadership extraction has been set to False')
            if "typ_Flag" not in prmpt_settings:
                prmpt_settings.typ_Flag = False
                print('type extraction has been set to False')
            if "subs_Flag" not in prmpt_settings:
                prmpt_settings.subs_Flag = False
                print('subsidiaries  extraction has been set to False')
            if "parnt_Flag" not in prmpt_settings:
                prmpt_settings.parnt_Flag = False
                print('parent extraction has been set to False')
    else:
            prmpt_settings.name_Flag = True
            prmpt_settings.id_Flag = True
            prmpt_settings.adrs_Flag = True
            prmpt_settings.lead_Flag = True
            prmpt_settings.typ_Flag = True
            prmpt_settings.subs_Flag = True
            prmpt_settings.parnt_Flag = True
            
    return prmpt_settings
            


# ==========================================================================

if __name__ == "__main__":
    
    parser = argparser_prompt()
    args = parser.parse_args()
    prmpt_settings = parser_prompt(args)
    
    #print(prmpt_settings)    
    prompt_question = get_prompt(prmpt_settings)
    print(prompt_question)
    
    
    
