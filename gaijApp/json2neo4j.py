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


def populate_graph_from_directory(directory_path, graph):
    companies_data = load_json_files(directory_path)

def populate_graph_from_directory(directory_path, graph):
    companies_data = load_json_files(directory_path)
    
    company_nodes = {}
    for data in tqdm(companies_data, desc="Creating company nodes"):
        # Check if company already exists in database
        company_id = data.get("company_id")
        if not company_id:
            continue
            
        existing = graph.nodes.match("Company", id=company_id).first()
        if existing:
            company_nodes[data.get("company_name")] = existing
            continue

        # Create node with safe data access
        company_node = Node(
            "Company",
            name=data.get("company_name", "Unknown"),
            id=company_id,
            address=data.get("company_address", ""),
            profit_status=data.get("profit_status", ""),
            number_of_employees=data.get("number_of_employees", "")
        )
        graph.merge(company_node, "Company", "id")
        company_nodes[data.get("company_name")] = company_node

        # Only create address node if address exists
        if data.get("company_address"):
            address_node = Node("Address", full_address=data["company_address"])
            graph.merge(address_node, "Address", "full_address")
            graph.merge(Relationship(company_node, "LOCATED_AT", address_node))

    for data in tqdm(companies_data, desc="Creating relationships"):
        company_name = data.get("company_name")
        if not company_name or company_name not in company_nodes:
            continue
            
        main_company = company_nodes[company_name]
        
        # Safe access to subsidiaries
        for subsidiary in data.get("subsidiaries", []):
            if subsidiary in company_nodes:
                graph.merge(Relationship(main_company, "PARENT_OF", company_nodes[subsidiary]))
            else:
                subsidiary_node = Node("Company", name=subsidiary)
                graph.merge(subsidiary_node, "Company", "name")
                graph.merge(Relationship(main_company, "PARENT_OF", subsidiary_node))

        # Safe access to parent company
        parent = data.get("parent_company")
        if parent and parent in company_nodes:
            graph.merge(Relationship(company_nodes[parent], "PARENT_OF", main_company))

        # Safe access to leadership data
        leadership = data.get("leadership", {})
        for role, person in [
            ("CEO", leadership.get("CEO")),
            ("Chairman", leadership.get("chairman_of_the_board"))
        ]:
            if person:
                person_node = Node("Person", name=person, role=role)
                graph.merge(person_node, "Person", "name")
                graph.merge(Relationship(person_node, "LEADS", main_company))

        # Safe access to board members
        for member in leadership.get("board_members", []):
            if member:
                member_node = Node("Person", name=member, role="Board Member")
                graph.merge(member_node, "Person", "name")
                graph.merge(Relationship(member_node, "MEMBER_OF", main_company))

        # Safe access to property ownership
        property_data = data.get("property_ownership", {})
        
        owned_properties = flatten_property_data(property_data.get("owns", []))
        for owned in owned_properties:
            if owned:
                property_node = Node("Property", name=owned)
                graph.merge(property_node, "Property", "name")
                graph.merge(Relationship(main_company, "OWNS", property_node))

        rented_properties = flatten_property_data(property_data.get("rents", []))
        for rented in rented_properties:
            if rented:
                property_node = Node("Property", name=rented)
                graph.merge(property_node, "Property", "name")
                graph.merge(Relationship(main_company, "RENTS", property_node))

def main():
    args = parse_args()
    graph = connect_to_neo4j()
    populate_graph_from_directory(args.data_dir, graph)
    print("Knowledge graph populated successfully!")

if __name__ == "__main__":
    main()
