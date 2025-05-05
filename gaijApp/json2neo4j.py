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
        neo4j_password = os.getenv('NEO4J_PASSWORD', 'testtest')
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

    def close(self):
        self.driver.close()

    def create_company(self, tx, company_data):
        # Clean the name field by filtering out None values if it's a list
        name = company_data.get("name")
        if isinstance(name, list):
            name = next((x for x in name if x is not None), "")
        else:
            name = name or ""

        # Clean the address field
        address = company_data.get("address")
        if isinstance(address, list):
            address = next((x for x in address if x is not None), "")
        else:
            address = address or ""

        # Clean the type field
        type_field = company_data.get("type")
        if isinstance(type_field, list):
            type_field = next((x for x in type_field if x is not None), "")
        else:
            type_field = type_field or ""

        query = """
        MERGE (c:Company {id: $id})
        SET c.name = $name,
            c.address = $address,
            c.type = $type
        RETURN c
        """
        return tx.run(query, 
                    id=company_data.get("ID"),
                    name=name,
                    address=address,
                    type=type_field)

    def create_address(self, tx, company_id, address):
        # Clean the address field
        if isinstance(address, list):
            address = next((x for x in address if x is not None), "")
        else:
            address = address or ""
            
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

    # def create_person_relationship(self, tx, person_name, company_id, role=None):
    #     query = """
    #     MATCH (c:Company {id: $company_id})
    #     MERGE (p:Person {name: $person_name})
    #     MERGE (p)-[:LEADS {role: $role}]->(c)
    #     """
    #     return tx.run(query, person_name=person_name, company_id=company_id, role=role)
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
        file_path = os.path.join(directory_path, filename)
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                json_data.append(json.load(file))
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    json_data.append(json.load(file))
            except json.JSONDecodeError as e:
                print(f"Skipping {filename} due to JSONDecodeError: {e}")
        except json.JSONDecodeError as e:
            print(f"Skipping {filename} due to JSONDecodeError: {e}")

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

            # Create leadership relationships - names only
            leadership = data.get("leadership", {})
            if leadership and isinstance(leadership, dict):
                names = leadership.get("names", [])
                if isinstance(names, str):
                    names = [names]
                    
                for leader_name in names:
                    if leader_name:
                        session.execute_write(
                            neo4j.create_person_relationship, 
                            leader_name, 
                            data["ID"]
                        )


             # Create leadership relationships with roles
            # leadership = data.get("leadership", {})
            # if leadership and isinstance(leadership, dict):
            #     roles = leadership.get("roles", [])
            #     if isinstance(roles, dict):
            #         roles = [roles]
                    
            #     for role_info in roles:
            #         if role_info and role_info.get("name"):
            #             session.execute_write(
            #                 neo4j.create_person_relationship, 
            #                 role_info["name"], 
            #                 data["ID"], 
            #                 role_info["role"]
            #             )
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
