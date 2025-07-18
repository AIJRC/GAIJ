# README - tax records analyzer 


## Overview:
This project extracts structured information from tax-related documents using an LLM-based prompt system. 
The architecture separates document processing from prompt inference to optimize performance and GPU resource allocation.

## Required architecture: 

### Server (GPU-enabled):

Handles API calls and performs inference using a large language model.
Minimum requirement: 48GB GPU memory.

### Local Machine / CPU Node

Preprocesses documents, sends prompts to the server, receives responses, and saves the output.

## How to run: 

### On the server: 

Start the API server via SLURM:
```cypher
sbatch run_API_job.slurm
```

### On the local Machine/CPU node:

Activate the virtual environment and run the processing script:

```cypher
source venv_llama/bin/activate
python main_server.py 
```
This script will:

	- Read the documents.
	- Send them to the server in the form of prompts.
	- Receive the extracted data.
	- Save the results in JSON format.

Optional Arguments:

	- Set input/output folders: Configure these in /app/config.
	- Limit the number of files to process (default is all files in the input folder):

```cypher
source venv_deepSeek/bin/activate
python main_server.py --run_nFiles <a number> 
```




