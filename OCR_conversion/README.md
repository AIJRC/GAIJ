# OCR and Company Detection Pipeline

This project contains tools for extracting text from images and detecting company names and other properties in the extracted text.

## Components

### 1. extract_text.py

This script uses OCR (Optical Character Recognition) to extract text from image files. It utilizes the tesserocr library for OCR processing.

Key features:
- Multithreaded processing for improved performance
- Supports TIF image format as input
- Outputs results in markdown format

### 2. look_for_companies.sh

This bash script searches for company names and other properties in the extracted text files.

Key features:
- Parallelized processing using GNU Parallel
- Configurable number of parallel processes
- Outputs results in CSV format with the same structure as the input file (one per file checked)

## Usage

### Extract Text

Run the extract_text.py script to perform OCR on image files:

`uv run OCR_conversion/extract_text.py --tifs_dir <input_directory> --md_dir <output_directory>`

### Detect Companies

Use the look_for_companies.sh script to search for company names:

`./OCR_conversion/look_for_companies.sh <folder_with_md_files> <path_to_companies_details.csv> <output_folder> [num_processes]`


## UV Tool

The uv tool is used in conjunction with this pipeline. To run the uv tool:

1. Ensure you have the necessary permissions and environment set up.
2. Navigate to the directory containing the uv tool.
3. Execute the uv tool with the appropriate command-line arguments:

`./uv [options] <input_files>`

Refer to the uv tool documentation for specific options and usage instructions.

## Requirements

- Python 3.x
- tesserocr library
- GNU Parallel

Ensure all dependencies are installed before running the scripts.
