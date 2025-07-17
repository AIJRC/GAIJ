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

## System Architecture

### Frontend
- Web portal interface
- Input form for company selection
- Property selection interface
- Visualization of company networks

### Backend
- LLM-based data extraction system
- JSON data processing
- Neo4j database integration
- Caching system for previously requested data

### Database
- Neo4j graph database
- Stores company relationships and properties
- Enables efficient network traversal

## MVP (Minimum Viable Product)

### Core Components
1. **Web Interface**
   - Company search input
   - Property selection checkboxes
   - Execute button
   - Basic graph visualization

2. **Backend Processing**
   - LLM prompt generation
   - Data extraction pipeline
   - JSON transformation

3. **Database**
   - Basic Neo4j schema
   - CRUD operations
   - Query optimization

## Development Roadmap

### Phase 1: Setup
- [ ] Initialize Neo4j database
- [ ] Create basic web interface
- [ ] Setup LLM integration

### Phase 2: Core Features
- [ ] Implement data extraction
- [ ] Develop JSON processing
- [ ] Create graph visualization

### Phase 3: Optimization
- [ ] Add caching system
- [ ] Improve query performance
- [ ] Enhance visualization

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
