# README - external API parser 


## Overview:

In this folder you can find the code necessary to parse the results from the external API endpoints for a batch of company ids.

the code contained in this folder will
- start a compute node with a GPU that will parse the results and exposes an API endpoint running the vLLM
- iterate from a company id list while calling the external APIs and create a prompt to send to the vLLM, and post-processes the results saving the resulting JSONs in a specified location

## Required architecture: 

### Server (GPU-enabled):

Handles API calls and performs inference using a large language model.
Minimum requirement: 48GB GPU memory.

### Local Machine / CPU Node

Preprocesses documents, sends prompts to the server, receives responses, and saves the output.

## How to run: 

### On the server: 

Start the API server via SLURM:
```
sbatch run_API_job.slurm
sbatch gaij/GAIJ/gaijApp/API_vLLM/external_API/run_API_job.slurm
```

or manually
```
srun --partition=gpu --gres=gpu:1 --pty bash
```
and inside you can run 
```
python -m vllm.entrypoints.openai.api_server --model '/home/gaij/.cache/huggingface/hub/models--meta-llama--Llama-3.2-1b-Instruct/snapshots/9213176726f574b556790deb65791e0c5aa438b6' --host 0.0.0.0 --port 8013 --max_model_len 65536

python -m vllm.entrypoints.openai.api_server \
  --model ~/models/llama-3.2-3b-instruct \
  --host 0.0.0.0 \
  --port 8013 \
  --max-model-len 8192

```

### On the local Machine/CPU node:

Activate the virtual environment and run the processing script:

```
source venv_llama/bin/activate
python main.py <path/to/csv/with/company/ids.csv> <output/folder/to/store/JSONs>
```

python main.py /home/gaij/data/metadata/metadata_1.csv /home/gaij/data/jsons/external
python main.py /home/gaij/data/metadata/metadata_6.csv /home/gaij/data/jsons/external


This script will:

	- Call the external API endpoints
	- Send them to the server in the form of prompts.
	- Receive the extracted data.
	- Save the results in JSON format.

