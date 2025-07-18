" load the configuration files "

import os 
import json 
import sys
from utils.support_functions import DotDict,Dic2DotDict
from utils.arg_parser import argparser_main,argparser_promptType,argparser_nFiles,parser_config,parser_nFiles

# Default configuration
config = {
    "save_directory": None,
    "load_directory": None,
    "error_directory":None}

def get_configuration():
    " check how has been the configuration been introduced "
    # check if arguments have been parsed   
    arg_folders = argparser_main()
    arg_prompt_type = argparser_promptType()
    arg_nFiles = argparser_nFiles()
    
    # check if folder parser empty
    if arg_folders is None:
        # load the config file
        config_folders = initianlize_confi_folders()
    else:
        print("Setting up configuration ... 0/1")
        print(" Getting folder configuration from user input...")
        # get the parsed arguments 
        # folders
        config_folders = parser_config(arg_folders)
        print(" Folder configuration finalized")
        
        
    # check if number of files parser empty 
    if arg_nFiles is None:
        config_folders.nFiles_r = -1
    else:
        nFiles = parser_nFiles(arg_nFiles)
        config_folders.nFiles_r = nFiles 
    print("Setting up configuration ..1/1... finished")
        

    return [config_folders]

def initianlize_confi_folders():
    """ 
    Initialize the configuration of paths  using the config file, 
        if the folders don't exits create the folders 
    """
    
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    print("Setting up configuration ... 0/1")
    
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
    print("Setting up configuration ..1/1... finished")
    return config


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
                print(f'  Created directory: {"output"}')
            except OSError as e:
                print(f'  Error creating directory: {e}')
                sys.exit()
        else: 
            try:
                os.makedirs(os.path.join("output",directory))
                print(f"  Created directory: {directory} inside output directory")
            except OSError as e:
                print(f"  Error creating directory: {e}")
                sys.exit()