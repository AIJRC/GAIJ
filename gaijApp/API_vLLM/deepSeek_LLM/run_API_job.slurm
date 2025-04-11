#!/bin/bash
#SBATCH --job-name=vllm_api
#SBATCH --partition=gpu
#SBATCH --gres=gpu:2
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --output=vllm_api_.log

# Optional: Load your Python environment or modules
source /home/gaij/venv_deepSeek/bin/activate

# Launch the API server
python3 -m vllm.entrypoints.openai.api_server \
    --model deepseek-ai/DeepSeek-R1-Distill-Llama-8B \
    --host 0.0.0.0 \
    --port 8000 \
    --max_model_len 30000 \
    --pipeline-parallel-size 2