# Configuration Setup

This document explains how to configure the system using environment variables via a `.env` file.


## Location

Create a file named `.env` in the `config/` directory or the root of the project. You can use `config/.env.example` as a starting point:

```bash
cp config/.env.example .env
```


## Environment Variables

| Variable           | Description                                 | Example                           |
|--------------------|---------------------------------------------|-----------------------------------|
| `NEO4J_URI`        | URI to the Neo4j database                   | `bolt://localhost:7687`           |
| `NEO4J_USER`       | Username for Neo4j                         | `neo4j`                           |
| `NEO4J_PASSWORD`   | Password for Neo4j                         | `your_password`                   |
| `LLM_API_KEY`      | API key for LLM provider (if remote)       | `sk-xxxxxx`                       |
| `LLM_PROVIDER`     | Name of the LLM provider (e.g. `openai`)   | `openai` or `llama`               |
| `OCR_ENGINE`       | OCR engine to use                          | `tesseract`                       |


## Tips

- Keep your `.env` file **out of version control** (`.gitignore`).
- Use a `.env.example` template to share with collaborators.
- Load environment variables at runtime using Python's `dotenv` or similar.


## Loading in Python

In your Python scripts:

```python
from dotenv import load_dotenv
load_dotenv()  # Loads variables from .env into os.environ
```

Now you can access them:

```python
import os
neo4j_uri = os.getenv("NEO4J_URI")
```
