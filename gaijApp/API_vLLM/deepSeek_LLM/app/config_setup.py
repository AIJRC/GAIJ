" load the configuration files "

import os 
import json 
import sys
from utils.support_functions import DotDict,Dic2DotDict
from prompts.prompt_manager import check_promptSettings
from utils.arg_parser import argparser_main,argparser_prompt_type,argparser_prompt_info,argparser_nFiles,parser_config,parser_prompt_info,parser_prompt_type,parser_nFiles

# Default configuration
config = {
    "save_directory": None,
    "load_directory": None,
    "error_directory":None}

prmpt_info_settings = DotDict()
prmpt_info_settings.NOR_Flag = False
prmpt_info_settings.AllFields_Flag = True



def get_configuration():
    " check how has been the configuration been introduced "
    # check if arguments have been parsed   
    arg_folders = argparser_main()
    arg_prompt_type = argparser_prompt_type()
    arg_prompt_info = argparser_prompt_info()
    arg_nFiles = argparser_nFiles()
    
    # check if folder parser empty
    if arg_folders is None:
        # load the config file
        config_folders = initianlize_confi_folders()
    else:
        print("Setting up configuration ... 0/2")
        print(" Getting folder configuration from user input...")
        # get the parsed arguments 
        # folders
        config_folders = parser_config(arg_folders)
        print(" Folder configuration finalized")
        print("Setting up configuration ..1/2")
        
    # check if number of files parser empty 
    if arg_nFiles is None:
        config_folders.nFiles_r = -1
    else:
        nFiles = parser_nFiles(arg_nFiles)
        config_folders.nFiles_r = nFiles 
        
    # check the prompt type parser is empty
    if arg_prompt_type is None:   
        # load the prompt file
        prmpt_settings = initialize_confi_prompt_type()
    else:
        print(" Getting prompt configuration from user input...")
        # get the parsed arguments 
        # prompt   
        prmpt_settings = parser_prompt_type(arg_prompt_type)
        
    
    # check if prompt parser is empty 
    if arg_prompt_info is None:   
        # load the prompt file
        prmpt_info_settings = initialize_confi_prompt_info()
    else:
        # get the parsed arguments 
        # prompt   
        prmpt_info_settings = parser_prompt_info(arg_prompt_info)
        print(" Prompt configuration finalized!")
        print("Setting up configuration ..2/2... finished")

    return [config_folders,prmpt_settings,prmpt_info_settings]

def initianlize_confi_folders():
    """ 
    Initialize the configuration of paths  using the config file, 
        if the folders don't exits create the folders 
    """
    
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    print("Setting up configuration ... 0/2")
    
     # Check if config file exists
    if os.path.exists(config_path):
        print(" Loading folder configuration from config.json...")
        with open(config_path, "r") as f:
            config = json.load(f)
            #config.update(json.load(f))
            config = DotDict(config)
        
    else:
        print(" No folder configuration file found. Setting up new configuration...")
        
        # save directory 
        config = DotDict()
        config.save_directory = mk_directory("save_directory")
        config.error_directory = mk_directory("error_directory")
        config.load_directory = get_directory("Enter the directory where files should be loaded from: ")
     
    print(" Folder configuration finalized")
    print("Setting up configuration ..1/2")
    return config


def initialize_confi_prompt_type():
    """ 
    Initialize the of prompt, using the config_prompt file, 
        if the prompt file does not exist create it
    """
    prmptConfig_path = os.path.join(os.path.dirname(__file__), "config_prompt_type.json")
    # check if the config_prompt_type file exists 
    if os.path.exists(prmptConfig_path):
        print(" Loading prompt configuration from config_prompt_type.json...")
        with open(prmptConfig_path, "r") as f:
            prmpt_settings = json.load(f)
        # convert it to a dot dictionary 
        prmpt_settings=Dic2DotDict(prmpt_settings)  #Dic2DotDict
        # check that the fields are correctly introduced
        prmpt_settings = check_promptSettings(prmpt_settings)    
        with open(prmptConfig_path, 'w') as json_file:
            json.dump(prmpt_settings, json_file, indent=4)
  
    else:
        print(" No prompt configuration file found. Setting up new configuration...")
        
        # save directory 
        prmpt_settings = DotDict()
        prmpt_settings.info_Flag = False
        prmpt_settings.notes_Flag = False
        prmpt_settings.redFlags_Flag = True
        # Save the JSON of prompt configuration to a file
        with open(prmptConfig_path, 'w') as json_file:
            json.dump(prmpt_settings, json_file, indent=4, ensure_ascii=False)  # Save the JSON with indentation for readability

    
    return prmpt_settings

def initialize_confi_prompt_info():
    """ 
    Initialize the of prompt, using the config_prompt file, 
        if the prompt file does not exist create it
    """
    prmptConfig_path = os.path.join(os.path.dirname(__file__), "config_prompt_info.json")
    # check if the config_prompt_info file exists 
    if os.path.exists(prmptConfig_path):
        print(" Loading prompt configuration from config_prompt_info.json...")
        with open(prmptConfig_path, "r") as f:
            prmpt_settings = json.load(f)
        # convert it to a dot dictionary 
        prmpt_settings=Dic2DotDict(prmpt_settings)  #Dic2DotDict
        # check that the fields are correctly introduced
        prmpt_settings = check_promptSettings(prmpt_settings)    
        with open(prmptConfig_path, 'w') as json_file:
            json.dump(prmpt_settings, json_file, indent=4)
  
    else:
        print(" No prompt configuration file found. Setting up new configuration...")
        
        # save directory 
        prmpt_settings = DotDict()
        prmpt_settings.NOR_Flag = False
        prmpt_settings.AllFields_Flag = True
        # Save the JSON of prompt configuration to a file
        with open(prmptConfig_path, 'w') as json_file:
            json.dump(prmpt_settings, json_file, indent=4, ensure_ascii=False)  # Save the JSON with indentation for readability
    print(" Prompt configuration finalized")
    print("Setting up configuration ..2/2... finished")
    
    return prmpt_settings

def get_directory(prompt):
        """
        Prompt the user for a directory path, ensuring it exists.
        """
        while True:
            directory = input(prompt).strip()
            if not os.path.exists(directory):
                print(f"  Error: The data directory does not exits, please try again")
            else:
                print(f"  Loading directory found : {directory}")
                return directory
        
    
def mk_directory(directory):
        """
        create the directory to store data

        Args:
            directory (str): name of directory 
        """
        if not os.path.exists("output"):
            try:
                os.makedirs("output")
                print(f"  Created directory: {"output"}")
            except OSError as e:
                print(f"  Error creating directory: {e}")
                sys.exit()
        else: 
            try:
                os.makedirs(os.path.join("output",directory))
                print(f"  Created directory: {directory} inside output directory")
            except OSError as e:
                print(f"  Error creating directory: {e}")
                sys.exit()