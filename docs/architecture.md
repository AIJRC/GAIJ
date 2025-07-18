# System Architecture

This project follows a modular pipeline architecture that transforms unstructured data into a structured knowledge graph. The high-level flow is as follows:

```
DATA → OCR → LLM → JSON → Neo4j → WebApp
```


## 1. OCR Module

- **Input**: PDF or image documents
- **Process**: Optical Character Recognition (OCR) extracts raw text.
- **Tool**: Tesseract or other OCR engines
- **Output**: Markdown text file


## 2. LLM Module

- **Input**: Extracted text
- **Process**: A Large Language Model parses text to extract entities and relationships.
- **Tool**: Can be OpenAI, LLaMA, or another local/integrated LLM
- **Output**: Structured JSON containing company data


## 3. JSON → Neo4j Loader

- **Input**: LLM-generated JSON
- **Process**: Data is transformed into Cypher queries and uploaded into Neo4j
- **Tool**: Custom Python script (see `data_pipeline/neo4j_loader`)
- **Output**: Populated graph database


## 4. Web Interface

- **Input**: Neo4j database
- **Process**: Queries and visualizes company relationships using a front-end application
- **Output**: Interactive graph explorer


## Design Principles

- Modular: Each step can be run independently
- Configurable: Environment-driven settings
- Expandable: Support for additional entity types or data sources
