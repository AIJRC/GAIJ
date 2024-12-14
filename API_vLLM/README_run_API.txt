How to API the the markdown data to the server using vLLM and Llama 

Step 1: 
	Activate the right environment in the NAIC server 
source vm-provision-scripts/cloud-init/projects/GAIJ/.venv-vLLM/bin/activate

Step 2: 
	
	Start the process in the server so the port 8000 is listening 
python -m vllm.entrypoints.openai.api_server --model /home/naic-user/Llama-3.2-3B-Instruct --host localhost --port 8000 --max_model_len 65536
	- To run it on the background: 
screen -S api_server 
python -m vllm.entrypoints.openai.api_server --model /home/naic-user/Llama-3.2-3B-Instruct --host localhost --port 8000 --max_model_len 65536
keys: Ctrl + D + A to detach it
	To reatach it (when needed)  
screen -r api_server 


Step 3: 
	Start a SSH brigde connection in another terminal 
ssh -i C:\Users\Oihane\.ssh\naic-key -L 8000:localhost:8000 naic-user@34.82.56.213 
	add -vv before the -i to make it verbose, in case of issues 

Step 4: 
	Run the code locally
python sendFiles2server_v1.py --md_dir 'directory where the markdown files are (optional) 
			      --out_dir 'directory where the JSON files wil be stored' (optional)
			      --error_dir 'in case a file can not be processed, directory where the ID of that file will be saved (optional) 
			      --run_nFiles ' number of files to run each batch, if empty all of the files that have not been processed will be run ( optional, but advised) 


To end the session: 
	- Reatach the process ( if screen has been used) 
screen -r api_server
keys: Ctrl + C 
	- Stop the SSH bridge connection: exit


Requirements: 
Pandas 
openpyxl
