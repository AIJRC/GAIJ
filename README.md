# GAIJ Applied to Norwegian Company Networks

**GAIJ** is a modular pipeline that extracts structured graph data from unstructured data and visualizes it in an interactive web interface using a Neo4j graph database. It uses a combination of OCR, LLMs, and knowledge graph tools to process documents and populate the database.

In this repo we showcase it with Norwegian tax records. GAIJ enables users to explore company relationships such as ownership, board membership, and subsidiaries. 

## Features

- Extracts:
  - Company name (Firmanavn)
  - Tax ID (Organisasjonsnummer)
  - Parent and subsidiary links
  - Board members and shareholders
  - Company address
  - Company type
- Modular components: OCR → LLM → Neo4j → Web App
- Web-based interactive graph viewer
- Configurable via environment variables


## Architecture

The system is built as a pipeline:

```
DATA → OCR → LLM → JSON → Neo4j → WebApp
```

Each stage is modular and can be run independently. See [`docs/architecture.md`](docs/architecture.md) for full details.


## Installation

1. **Configure environment**  
   See [`docs/config_setup.md`](docs/config_setup.md) to set up your `.env` file.

2. **Start services**  
   Refer to [`docs/usage_guide.md`](docs/usage_guide.md) for running the pipeline and launching the app.


## Requirements

- Python 3.11+
- Neo4j database
- OCR tool (e.g., Tesseract)
- LLM service or local model
- Modern web browser (for frontend)


## Documentation

- [`docs/architecture.md`](docs/architecture.md) – System overview
- [`docs/usage_guide.md`](docs/usage_guide.md) – How to run the pipeline
- [`docs/config_setup.md`](docs/config_setup.md) – Setting up environment variables


# Miscellaneous Instructions

## Accessing Neo4j Console

On the server, you can access the Neo4j database console using:

```bash
sudo docker exec -it neo4j cypher-shell -u neo4j -p testtest
```

Once connected, you can manually query the database. See the file `cypher_commands_query_db.md` for query examples.

---

## Importing JSON Files into Neo4j

The script `json2neo4j.py` will scan a directory of JSON files and populate the Neo4j database.

### Step-by-Step

1. **Ensure the Neo4j Docker container is running** and is named `neo4j`.

2. **Prepare your data directory** so that it includes the following subfolders:
    - `external/`
    - `llama/`
    - `red_flags/`

3. **Run the import script**:

```bash
python3 json2neo4j.py --data-dir ~/data/jsons/
```


---

## (Optional) Wipe the Database Before Importing

If you want to start with a clean database (e.g., for testing or to avoid stale data), you can wipe it before importing:

1. **Access Neo4j shell**:

```bash
sudo docker exec -it neo4j cypher-shell -u neo4j -p testtest
```

2. **Run this command to delete all nodes and relationships**:

```cypher
MATCH (n)
WITH n LIMIT 100000
DETACH DELETE n;
```
repeat until no durther data is available

**Warning:** This will completely erase all data in the graph.

---

## Notes

- The script uses `MERGE` to avoid creating duplicate nodes and relationships.
- Running the script multiple times **will update existing data** but **won’t remove properties** that have been removed from the source files. Use the wipe step above for a clean refresh.
