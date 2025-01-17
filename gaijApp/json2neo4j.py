from neo4j import GraphDatabase
import json
import os
import argparse
from tqdm import tqdm

def parse_args():
    parser = argparse.ArgumentParser(description='Process JSON files to Neo4j database')
    parser.add_argument('--data-dir', type=str, required=True, help='Directory containing JSON files')
    return parser.parse_args()

class Neo4jConnector:
    def __init__(self):
        neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
        neo4j_password = os.getenv('NEO4J_PASSWORD', 'password')
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

    def close(self):
        self.driver.close()

    def create_company(self, tx, company_data):
        query = """
        MERGE (c:Company {id: $id})
        SET c.name = $name,
            c.address = $address,
            c.type = $type
        RETURN c
        """
        return tx.run(query, 
                     id=company_data.get("ID"),
                     name=company_data.get("name")[0] if isinstance(company_data.get("name"), list) else company_data.get("name"),
                     address=company_data.get("address", ""),
                     type=company_data.get("type", ""))

    def create_address(self, tx, company_id, address):
        query = """
        MATCH (c:Company {id: $company_id})
        MERGE (a:Address {full_address: $address})
        MERGE (c)-[:LOCATED_AT]->(a)
        """
        return tx.run(query, company_id=company_id, address=address)

    def create_relationship(self, tx, from_id, to_name, rel_type):
        query = f"""
        MATCH (c1:Company {{id: $from_id}})
        MERGE (c2:Company {{name: $to_name}})
        MERGE (c1)-[:{rel_type}]->(c2)
        """
        return tx.run(query, from_id=from_id, to_name=to_name)

    def create_person_relationship(self, tx, person_name, company_id):
        query = """
        MATCH (c:Company {id: $company_id})
        MERGE (p:Person {name: $person_name})
        MERGE (p)-[:LEADS]->(c)
        """
        return tx.run(query, person_name=person_name, company_id=company_id)

def load_json_files(directory_path):
    json_data = []
    files = [f for f in os.listdir(directory_path) if f.endswith('.json')]
    
    for filename in tqdm(files, desc="Loading JSON files"):
        try:
            with open(os.path.join(directory_path, filename), 'r', encoding='utf-8-sig') as file:
                json_data.append(json.load(file))
        except UnicodeDecodeError:
            with open(os.path.join(directory_path, filename), 'r', encoding='latin-1') as file:
                json_data.append(json.load(file))
    return json_data

def populate_graph_from_directory(directory_path, neo4j):
    companies_data = load_json_files(directory_path)
    
    with neo4j.driver.session() as session:
        for data in tqdm(companies_data, desc="Processing companies"):
            if not data.get("ID") or not data.get("name"):
                continue

            # Create company node
            session.execute_write(neo4j.create_company, data)

            # Create address relationship
            if data.get("address"):
                session.execute_write(neo4j.create_address, data["ID"], data["address"])

            # Create subsidiary relationships
            subsidiaries = data.get("subsidiaries", []) or []  # Default to empty list if None
            if isinstance(subsidiaries, str):
                subsidiaries = [subsidiaries]
            for subsidiary in subsidiaries:
                if subsidiary:
                    session.execute_write(neo4j.create_relationship, data["ID"], subsidiary, "PARENT_OF")

            # Create parent relationships
            parents = data.get("parent", []) or []  # Default to empty list if None
            if isinstance(parents, str):
                parents = [parents]
            for parent in parents:
                if parent:
                    session.execute_write(neo4j.create_relationship, data["ID"], parent, "PARENT_OF")

            # Create leadership relationships
            leaders = data.get("leadership", []) or []  # Default to empty list if None
            if isinstance(leaders, str):
                leaders = [leaders]
            for leader in leaders:
                if leader:
                    session.execute_write(neo4j.create_person_relationship, leader, data["ID"])

def main():
    args = parse_args()
    neo4j = Neo4jConnector()
    try:
        populate_graph_from_directory(args.data_dir, neo4j)
        print("Knowledge graph populated successfully!")
    finally:
        neo4j.close()

if __name__ == "__main__":
    main()
