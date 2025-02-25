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


from app.config_setup import initianlize_confi_folders,initialize_confi_prompt,get_configuration
#from scripts.run_LLM_server import files_loop
from scripts.run_LLM_local import files_loop
from documents.document_manager import whichfiles
from utils.arg_parser import argparser_main,argparser_prompt,parser_config,parser_prompt



def vLLM_remote():
    """ Main function to run a list of files located in a directory through vLLM 
     extract certain data and save it in a JSON format in another directory
     """
     
    [config,prmpt_settings] = get_configuration() 
    
    #config = Dic2DotDict(config)
    # get the folders 
    input_dir = config.load_directory
    out_dir = config.save_directory
    err_dir = config.error_directory
    if "nFiles_r" in config:
        nFiles_r = config.nFiles_r
    else:
        nFiles_r = -1
        
    # ====== get the list of files to be processed 
    files_list = whichfiles(input_dir,out_dir)
    # ====== Loop through the files and send to server 
    files_loop(files_list,input_dir,out_dir,err_dir,nFiles_r,prmpt_settings)
    
#vLLM_remote(config,prmpt_settings)

# ========== 

if __name__ == "__main__":
   
    # Run the main process 
    vLLM_remote()

    
    
    
    
        
    