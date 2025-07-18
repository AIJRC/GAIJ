# GAIJ Web Application

GAIJ is a FastAPI-based web application that allows users to compute properties of a Neo4j graph and visualize it interactively. This guide explains how to install dependencies and start the web app locally or on a server.

---

## Prerequisites

Ensure you have the following installed on your system:

1. **Python**: Version 3.9 or higher.

---

## Installation Instructions

### 1. Clone the Repository
Clone this GitHub repository to your local machine:


### 2. Set Up a Virtual Environment (Optional)
For dependency isolation, create and activate a virtual environment:
```bash
# Create virtual environment
python3.12 -m venv .venv-web-app

# Activate the virtual environment
source .venv-web-app/bin/activate 
```

### 3. Install Dependencies
Install the required Python dependencies using `pip`:
```bash
pip install -r requirements.txt
```

---

## Starting the Web App

### Locally
1. Run the FastAPI web app using `uvicorn`:
   ```bash
   uvicorn app.main:app --reload
   ```
2. Open your browser and navigate to:
   ```
   http://127.0.0.1:8000
   ```

### On a Server
To deploy on a production server, use `gunicorn` with an ASGI worker such as `uvicorn.workers.UvicornWorker`. For example:
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Features

1. **Compute Properties**:
   - Define new properties for nodes in the graph.
   - Track ongoing computations with real-time updates.

2. **Visualize Graph**:
   - View nodes and relationships interactively.
   - Focus on specific nodes, properties, or relationship types.

---

## Contribution Guidelines

Feel free to fork the repository, open issues, or submit pull requests to contribute to this project.