Modular pipeline to extract structured graphs from unstructured text and explore them via a web-based interface.

# GAIJ - Norwegian Company Network Analyzer

## Project Overview
GAIJ is a web-based application that visualizes company relationships and properties using Neo4j graph database. The system extracts data from Norwegian tax records and presents interconnected company information in an interactive graph format.

## Features
### Data Properties
Currently the GAIJ system extracts the following company properties:
- Company Name (Firmanavn)
- Tax Number (Organisasjonsnummer)
- Parent Company (Morselskap)
- Subsidiary Companies (Datterselskaper)
- Address (Adresse)
- Board Members and Shareholders (Styremedlemmer og Aksjeeiere)
- Company Type (Organisasjonsform)


## Technical Requirements
- Neo4j database
- Web server
- LLM integration
- Graph visualization library



# Instructions

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

Replace `/path/to/your/data` with the full path to the folder containing the JSON subdirectories.

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
