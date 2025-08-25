#!/bin/bash
#SBATCH --partition=gpu
#SBATCH --job-name=cpu_client
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G


# Activate your environment
source /home/gaij/venv_deepseek/bin/activate

# Run your Python client
python codes/deepseek/main_server.py
