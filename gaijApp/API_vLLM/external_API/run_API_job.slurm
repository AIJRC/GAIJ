#!/bin/bash
#SBATCH --job-name=vllm_api_external
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --output=vllm_api_external_.log

# Optional: Load your Python environment or modules
source /home/gaij/venv_llama/bin/activate

# Launch the API server
python -m vllm.entrypoints.openai.api_server \
    --model '/home/gaij/.cache/huggingface/hub/models--meta-llama--Llama-3.2-1b-Instruct/snapshots/9213176726f574b556790deb65791e0c5aa438b6'\
    --host 0.0.0.0 \
    --port 8000 \
    --max_model_len 65536