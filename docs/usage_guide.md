# Usage Guide

This guide walks you through running each component of the GAIJ pipeline.


## 1. Prerequisites

Make sure the following are installed:

- Python 3.11+
- Neo4j database (local or remote)
- OCR tool (e.g. Tesseract)
- `.env` file with required variables (see [Configuration Setup](config_setup.md))


## 2. Environment Setup

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```


## 3. OCR: Extract Text

Run the OCR module to convert PDFs/images into raw text:

```bash
python data_pipeline/ocr/extract_text.py --input data/input.pdf --output data/output.txt
```


## 4. LLM: Extract Structured Data

Use the LLM to convert text into JSON-structured data:



## 5. Load into Neo4j

Load the JSON into your Neo4j instance:



## 6. Launch the Web App

Start the web app to explore the graph:

```bash
cd web-app
streamlit run app.py
```

Ensure the `NEO4J_URI`, `NEO4J_USER`, and `NEO4J_PASSWORD` are set in your `.env`.
