""" argument parser unit """

import argparse
from argparse import Namespace
from utils.support_functions import DotDict


def argparser_main():
    " parser with the folder configuration"
    parser = argparse.ArgumentParser(description='text data extraction - vllm')
    # General settings 
    parser.add_argument('--md_dir', required=False, help='directory with the markdown files to be processed')
    parser.add_argument('--out_dir', required=False, help='Output directory for JSON file ')
    parser.add_argument('--error_dir', required=False, help='Output directory for file wth error files (optional) ')
    args,unknown = parser.parse_known_args()
    
    # check wether any argument has been introduced 
    [cnt,emptyCont] = count_emptyArgs(args)
    if emptyCont == cnt:
        args = None 
    
    return args 

def argparser_nFiles():
    " parser with the number of files to process "
    parser = argparse.ArgumentParser(description='number of files fo run')
    parser.add_argument('--run_nFiles', required=False, help='number of Files to run each batch, default -1-> all')
    args,unknown = parser.parse_known_args()
    
    # check wether any argument has been introduced 
    [cnt,emptyCont] = count_emptyArgs(args)
    if emptyCont == cnt:
        args = None 
    
    return args 

def argparser_promptType():
    " parser with the info about the prompt type will be used for data extraction"
    parser = argparse.ArgumentParser(description='prompt selection for LLMM')
    parser.add_argument('--notes_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask for the prompt to be in Norwegian - default FALSE')
    parser.add_argument('--redFlags_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask for the prompt to be in Norwegian - default FALSE')
    args,unknown = parser.parse_known_args()
    # check wether any argument has been introduced 
    [cnt,emptyCont] = count_emptyArgs(args)
    if emptyCont == cnt:
        args = None 
    
    return args
    
def parser_config(args):
    """ deals with the arguments from the configuration:
    folers and files to run """
    config = DotDict()
    # count the empty fields 
    emptyCont = 0
    # ===== get the arguments - General settings
        # input (markdown files)
    if args.md_dir:
        config.load_directory = args.md_dir
    else:
        emptyCont +=1
        config.load_directory = '/home/gaij/data/markdowns/'
        # output ( JSON files)
    if args.out_dir:
        config.save_directory = args.out_dir
    else:
        emptyCont +=1
        config.save_directory = '/home/gaij/data/jsons/red_flags/'
        # error ( txt files)
    if args.error_dir:
        config.error_directory = args.error_dir
    else:
        emptyCont +=1
        config.error_directory = '/home/gaij/data/error_files/'    
    return config

def parser_nFiles(args):
    """ deals with the argument of number of files """
    if args.run_nFiles:
        nFiles_r = int(args.run_nFiles)
    else:
        emptyCont +=1
        nFiles_r = -1
        
    return nFiles_r 


def parser_prompt_type(args):
    # Create a prompt setting arguments  that supports dot notation 
    prmpt_settings = DotDict()    
    # ===== get the arguments - prompt settings
    
    # Flag to a prompt to extract a summary of the notes 
    if args.notes_Flag is not None:
        prmpt_settings.notes_Flag = args.notes_Flag  
    else:
        prmpt_settings.notes_Flag = False
    # Flag to a prompt to extract a information  about the red flags provided by the journalists 
    if args.redFlags_Flag is not None:
        prmpt_settings.redFlags_Flag = args.redFlags_Flag  
    else:
        prmpt_settings.redFlags_Flag = True
    
def count_emptyArgs(args):        
    emptyCont = 0
    cnt = 0
    for arg, value in vars(args).items():
        cnt +=1 
        if value is None:
            emptyCont +=1

    return[cnt,emptyCont]
