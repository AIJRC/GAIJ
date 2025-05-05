#!/bin/bash
#SBATCH --job-name=vllm_api_external
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --output=vllm_api_external_.log

# Optional: Load your Python environment or modules
source /home/gaij/venv_llama/bin/activate

python -m vllm.entrypoints.openai.api_server \
  --model /home/gaij/models/llama-3.2-3b-instruct \
  --host 0.0.0.0 \
  --port 8013 \
  --max-model-len 8192
