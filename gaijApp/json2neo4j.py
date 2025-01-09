from py2neo import Graph, Node, Relationship
import json
import os
import argparse
from tqdm import tqdm

def parse_args():
    parser = argparse.ArgumentParser(description='Process JSON files to Neo4j database')
    parser.add_argument('--data-dir', type=str, required=True, help='Directory containing JSON files')
    return parser.parse_args()

def connect_to_neo4j():
    neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
    neo4j_password = os.getenv('NEO4J_PASSWORD', 'password')
    return Graph(neo4j_uri, auth=(neo4j_user, neo4j_password))

def load_json_files(directory_path):
    json_data = []
    files = [f for f in os.listdir(directory_path) if f.endswith('.json')]
    
    for filename in tqdm(files, desc="Loading JSON files"):
        try:
            # First try with utf-8-sig
            with open(os.path.join(directory_path, filename), 'r', encoding='utf-8-sig') as file:
                json_data.append(json.load(file))
        except UnicodeDecodeError:
            # If that fails, try with latin-1
            with open(os.path.join(directory_path, filename), 'r', encoding='latin-1') as file:
                json_data.append(json.load(file))
    return json_data


def flatten_property_data(property_data):
    """Extract property names from nested structures"""
    if isinstance(property_data, str):
        return [property_data]
    if isinstance(property_data, dict):
        properties = []
        for value in property_data.values():
            properties.extend(flatten_property_data(value))
        return properties
    if isinstance(property_data, list):
        properties = []
        for item in property_data:
            properties.extend(flatten_property_data(item))
        return properties
    return []


# def populate_graph_from_directory(directory_path, graph):
#     companies_data = load_json_files(directory_path)

def populate_graph_from_directory(directory_path, graph):
    companies_data = load_json_files(directory_path)
    
    company_nodes = {}
    for data in tqdm(companies_data, desc="Creating company nodes"):
        # Check if company already exists in database
        company_id = data.get("ID")
        company_name = data.get("name")

         # Handle case where name is a list
        if isinstance(company_name, list):
            company_name = company_name[0] if company_name else None
            
        if not company_id or not company_name:
            continue
            
        existing = graph.nodes.match("Company", id=company_id).first()
        if existing:
            company_nodes[company_name] = existing
            continue
        # Create node with new structure
        company_node = Node(
            "Company",
            name=data.get("name", "Unknown"),
            id=company_id,
            address=data.get("address", ""),
            type=data.get("type", "")
        )
        graph.merge(company_node, "Company", "id")
        company_nodes[data.get("name")[0]] = company_node

        # Create address node if address exists
        if data.get("address"):
            address_node = Node("Address", full_address=data["address"])
            graph.merge(address_node, "Address", "full_address")
            graph.merge(Relationship(company_node, "LOCATED_AT", address_node))

    for data in tqdm(companies_data, desc="Creating relationships"):
        company_name = data.get("name")[0]
        if not company_name or company_name not in company_nodes:
            continue
            
        main_company = company_nodes[company_name]
        
        subsidiaries = data.get("subsidiaries", [])
        if type(subsidiaries) == list:
            for subsidiary in subsidiaries:
                if subsidiary in company_nodes:
                    graph.merge(Relationship(main_company, "PARENT_OF", company_nodes[subsidiary]))
                else:
                    subsidiary_node = Node("Company", name=subsidiary)
                    graph.merge(subsidiary_node, "Company", "name")
                    graph.merge(Relationship(main_company, "PARENT_OF", subsidiary_node))
        elif type(subsidiaries) == str:
            if subsidiaries in company_nodes:
                graph.merge(Relationship(main_company, "PARENT_OF", company_nodes[subsidiaries]))
            else:
                subsidiary_node = Node("Company", name=subsidiaries)
                graph.merge(subsidiary_node, "Company", "name")
                graph.merge(Relationship(main_company, "PARENT_OF", subsidiary_node))

        # Handle parent company
        parents = data.get("parent",[])
        if type(parents) == list:
            for parent in parents:
                if parent and parent in company_nodes:
                    graph.merge(Relationship(company_nodes[parent], "PARENT_OF", main_company))
                else:
                    parent_node = Node("Company", name=parent)
                    graph.merge(parent_node, "Company", "name")
                    graph.merge(Relationship(parent_node, "PARENT_OF", main_company))
        elif type(parents) == str:
                if parents and parents in company_nodes:
                    graph.merge(Relationship(company_nodes[parents], "PARENT_OF", main_company))
                else:
                    parent_node = Node("Company", name=parents)
                    graph.merge(parent_node, "Company", "name")
                    graph.merge(Relationship(parent_node, "PARENT_OF", main_company))
            

        leaders = data.get("leadership", [])
        if type(leaders) == list:
            for leader in leaders:
                if leader:
                    # Check if person already exists
                    existing_person = graph.nodes.match("Person", name=leader).first()
                    if existing_person:
                        person_node = existing_person
                    else:
                        person_node = Node("Person", name=leader)
                        graph.merge(person_node, "Person", "name")

                    # Create relationship if it doesn't exist
                    if not graph.match((person_node, main_company), "LEADS").first():
                        graph.merge(Relationship(person_node, "LEADS", main_company))
        else:
            if leaders:
                # Check if person already exists
                existing_person = graph.nodes.match("Person", name=leaders).first()
                if existing_person:
                    person_node = existing_person
                else:
                    person_node = Node("Person", name=leaders)
                    graph.merge(person_node, "Person", "name")


def main():
    args = parse_args()
    graph = connect_to_neo4j()
    populate_graph_from_directory(args.data_dir, graph)
    print("Knowledge graph populated successfully!")

if __name__ == "__main__":
    main()
