""" argument parser unit """

import argparse
from argparse import Namespace
from utils.support_functions import DotDict


def argparser_main():
    parser = argparse.ArgumentParser(description='text data extraction - vllm')
    # General settings 
    parser.add_argument('--md_dir', required=False, help='directory with the markdown files to be processed')
    parser.add_argument('--out_dir', required=False, help='Output directory for JSON file ')
    parser.add_argument('--error_dir', required=False, help='Output directory for file wth error files (optional) ')
    #parser.add_argument('--run_nFiles', required=False, help='number of Files to run each batch, default -1-> all')
    # Prompt settings 
    #parser.add_argument('--NOR_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask for the prompt to be in Norwegian - default FALSE')
    #parser.add_argument('--AllFields_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask to select all the information files of the prompt - default TRUE')
    #parser.add_argument('--name_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask to extract the Name of the company - default TRUE only available if AllFields_Flag==FALSE')
    #parser.add_argument('--id_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask to extract the ID of the company - default TRUE only available if AllFields_Flag==FALSE')
    #parser.add_argument('--adrs_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask to extract the Address of the company - default TRUE only available if AllFields_Flag==FALSE')
    #parser.add_argument('--typ_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask to extract the Type of company - default TRUE only available if AllFields_Flag==FALSE')
    #parser.add_argument('--lead_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask to extract the Leadership of the company - default TRUE only available if AllFields_Flag==FALSE')
    #parser.add_argument('--subs_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask to extract the subsidiaries of the company - default TRUE only available if AllFields_Flag==FALSE')
    #parser.add_argument('--parnt_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask to extract the Parent company of the company - default TRUE only available if AllFields_Flag==FALSE')
    #parser.add_argument('--id_Flag',type=lambda x: x.lower() in ['true', '1', 'yes'], required=False, help='Flag to ask to extract the ID of the company - default TRUE only available if AllFields_Flag==FALSE')
    args,unknown = parser.parse_known_args()
    
    # check wether any argument has been introduced 
    [cnt,emptyCont] = count_emptyArgs(args)
    if emptyCont == cnt:
        args = None 
    
    return args 

def argparser_nFiles():
    parser = argparse.ArgumentParser(description='number of files fo run')
    parser.add_argument('--run_nFiles', required=False, help='number of Files to run each batch, default -1-> all')
    args,unknown = parser.parse_known_args()
    
    # check wether any argument has been introduced 
    [cnt,emptyCont] = count_emptyArgs(args)
    if emptyCont == cnt:
        args = None 
    
    return args 

def argparser_prompt():
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
    args,unknown = parser.parse_known_args()
    # check wether any argument has been introduced 
    #emptyCont = 0
    #cnt = 0
    #for key, value in vars(args).items():
    #    cnt =+1 
    #    if value is None:
    #        emptyCont +=1
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
        config.load_directory = '/home/naic-user/data/markdowns/'
        #config.load_directory = 'F:\\Oihane\\OsloMet\\data\\markdown\\check_Lang'
        #input_dir = 'F:\\Oihane\\OsloMet\\data\\markdown\\check_Lang'
        # input_dir = 'F:\User\markdowns'
        # output ( JSON files)
    if args.out_dir:
        config.save_directory = args.out_dir
    else:
        emptyCont +=1
        config.save_directory = '/home/naic-user/data/jsons/'
        #config.save_directory = 'F:\\Oihane\\OsloMet\\data\\JSON\\check_Lang\\NOR\\test'
        #out_dir = 'F:\\Oihane\\OsloMet\\data\\JSON\\NOR_prompt'
        #out_dir = 'F:\\Oihane\\OsloMet\\data\\JSON\\check_Lang\\NOR'
        #out_dir = 'F:\\Oihane\\OsloMet\\data\\JSON\\check_Lang\\ENG'
        # out_dir = 'F:\User\JSON
        # error ( txt files)
    if args.error_dir:
        config.error_directory = args.error_dir
    else:
        emptyCont +=1
        config.error_directory = '/home/naic-user/data/error_files/'
        # err_dir = 'F:\User\errorFiles'
        # number of files to run 
    #if args.run_nFiles:
    #    config.nFiles_r = int(args.run_nFiles)
    #else:
    #    emptyCont +=1
    #    config.nFiles_r = -1    
    
    # check if it was empty 
    
        
    return config

def parser_nFiles(args):
    """ deals with the argument of number of files """
    if args.run_nFiles:
        nFiles_r = int(args.run_nFiles)
    else:
        emptyCont +=1
        nFiles_r = -1
        
    return nFiles_r 

def parser_prompt(args):
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

    return(prmpt_settings)
    
def count_emptyArgs(args):        
    emptyCont = 0
    cnt = 0
    for arg, value in vars(args).items():
        cnt +=1 
        if value is None:
            emptyCont +=1

    return[cnt,emptyCont]
