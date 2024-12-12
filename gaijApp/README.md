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