from neo4j import GraphDatabase
import json
import os
import argparse
from pathlib import Path
from tqdm import tqdm
from collections import defaultdict

def parse_args():
    parser = argparse.ArgumentParser(description='Process JSON files to Neo4j database')
    parser.add_argument('--data-dir', type=str, required=True, help='Directory containing JSON files')
    return parser.parse_args()

class Neo4jConnector:
    def __init__(self):
        neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
        neo4j_password = os.getenv('NEO4J_PASSWORD', 'testtest')
        if not neo4j_password:
            raise ValueError("NEO4J_PASSWORD environment variable is not set")
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

    def close(self):
        self.driver.close()
    
    def create_company(self, tx, company_data):
        props = {k: v for k, v in company_data.items() if v is not None}
        set_clause = ",\n            ".join([f'c.`{k}` = ${k}' for k in props])
        query = f"""
        MERGE (c:Company {{id: $id}})
        SET {set_clause}
        RETURN c
        """
        # print(query, props)
        return tx.run(query, **props)

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


def load_company_jsons(base_path):
    folders = ['external', 'llama', 'red_flags']
    # folders = ['external']
    # folders = ['red_flags']

    company_data = defaultdict(dict)

    for folder in folders:
        folder_path = os.path.join(base_path, folder)
        files = [f.name for f in Path(folder_path).glob('*.json')]
        # files = files[:100]
        for filename in tqdm(files, desc=f"Loading from {folder}"):
            try:
                filepath = os.path.join(folder_path, filename)
                with open(filepath, 'r', encoding='utf-8-sig') as file:
                    data = json.load(file)
            except UnicodeDecodeError:
                with open(filepath, 'r', encoding='latin-1') as file:
                    data = json.load(file)
            except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
                print(f"Error processing {filepath}: {str(e)}")
                continue

            company_id = filename.split('_')[0]
            company_data[company_id][folder] = data

    return company_data

def transform_property(value):
    """Recursively convert Maps or list of Maps to strings, and remove None from lists or dictionaries."""
    if isinstance(value, dict):  # If it's a map (dictionary)
        # Recursively clean the dictionary
        cleaned_dict = {k: transform_property(v) for k, v in value.items() if v is not None}
        return json.dumps(cleaned_dict)  # Return JSON string representation of the cleaned map
    elif isinstance(value, list):  # If it's a list
        # Remove None values and recursively apply transformation to each item
        cleaned_list = [transform_property(item) for item in value if item is not None]
        return cleaned_list  # Return the cleaned list
    else:  # If it's a primitive value, return it as is
        return value

def parse_flag(value):
    """Return the boolean value of the 'flag' key, handling 'true' string as True and other values as False."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == "true"  # Only "true" (case insensitive) returns True
    return False  # Everything else (None, empty, etc.) is False

def flatten_keys(d):
    """Flatten nested structures by replacing '.' with '_', and transform values."""
    return {
        k.replace('.', '_'): transform_property(v) for k, v in d.items()
    }

def populate_graph_from_directory(directory_path, neo4j):
    companies_data = load_company_jsons(directory_path)

    with neo4j.driver.session() as session:
        for company_id, data_sources in tqdm(companies_data.items(), desc="Processing companies"):
            external = data_sources.get("external", {})
            # print(external)
            llama = data_sources.get("llama", {})
            # print(llama)
            red_flags = data_sources.get("red_flags", {})
            # print(red_flags)

            if not external.get("company_id") and not llama.get("ID") and not red_flags:
                print(f"[WARNING] No data found for {company_id}. Skipping.")
                continue

            base_data = {"id": company_id}

            if external:
                base_data.update(flatten_keys({
                    "ext.company_name": external.get("company_name"),
                    "ext.company_address": external.get("company_address"),
                    "ext.company_type": external.get("company_type"),
                    "ext.leadership.CEO": external.get("leadership", {}).get("CEO"),
                    "ext.leadership.board_members": external.get("leadership", {}).get("board_members"),
                    "ext.leadership.share_holders": external.get("leadership", {}).get("share_holders"),
                    "ext.leadership.chairman_of_the_board": external.get("leadership", {}).get("chairman_of_the_board"),
                    "ext.subsidiaries": external.get("subsidiaries"),
                    "ext.parent_company": external.get("parent_company"),
                    "ext.auditor_name": external.get("auditor_name"),
                }))
            
            if llama:
                base_data.update(flatten_keys({
                    "company_name": llama.get("company_name"),
                    "company_address": llama.get("company_address"),
                    "company_type": llama.get("company_type"),
                    "leadership.CEO": llama.get("leadership", {}).get("CEO"),
                    "leadership.board_members": llama.get("leadership", {}).get("board_members"),
                    "leadership.share_holders": llama.get("leadership", {}).get("share_holders"),
                    "leadership.chairman_of_the_board": llama.get("leadership", {}).get("chairman_of_the_board"),
                    "subsidiaries": llama.get("subsidiaries"),
                    "parent_company": llama.get("parent_company"),
                    "auditor_name": llama.get("auditor_name"),
                    "version_control": llama.get("version_control"),
                }))
            
            if red_flags:


                base_data.update(flatten_keys({
                    "finance.unclear_instruments.flag": parse_flag(red_flags.get("finance", {}).get("unclear_instruments", {}).get("flag")),
                    "finance.unclear_instruments.details": red_flags.get("finance", {}).get("unclear_instruments", {}).get("details"),
                    
                    "finance.hidden_leasing.flag": parse_flag(red_flags.get("finance", {}).get("hidden_leasing", {}).get("flag")),
                    "finance.hidden_leasing.details": red_flags.get("finance", {}).get("hidden_leasing", {}).get("details"),

                    "finance.guarantee.flag": parse_flag(red_flags.get("finance", {}).get("guarantee", {}).get("flag")),
                    "finance.guarantee.details": red_flags.get("finance", {}).get("guarantee", {}).get("details"),

                    "finance.balance_values.flag": parse_flag(red_flags.get("finance", {}).get("balance_values", {}).get("flag")),
                    "finance.balance_values.details": red_flags.get("finance", {}).get("balance_values", {}).get("details"),

                    "finance.dependency.flag": parse_flag(red_flags.get("finance", {}).get("dependency", {}).get("flag")),
                    "finance.dependency.details": red_flags.get("finance", {}).get("dependency", {}).get("details"),

                    "transactions.one_off_expense.flag": parse_flag(red_flags.get("transactions", {}).get("one_off_expense", {}).get("flag")),
                    "transactions.one_off_expense.details": red_flags.get("transactions", {}).get("one_off_expense", {}).get("details"),

                    "transactions.internal_transactions.flag": parse_flag(red_flags.get("transactions", {}).get("internal_transactions", {}).get("flag")),
                    "transactions.internal_transactions.details": red_flags.get("transactions", {}).get("internal_transactions", {}).get("details"),

                    "transactions.outstanding_receivables.flag": parse_flag(red_flags.get("transactions", {}).get("outstanding_receivables", {}).get("flag")),
                    "transactions.outstanding_receivables.details": red_flags.get("transactions", {}).get("outstanding_receivables", {}).get("details"),

                    "accounting.auditor_reservations.flag": parse_flag(red_flags.get("accounting", {}).get("auditor_reservations", {}).get("flag")),
                    "accounting.auditor_reservations.details": red_flags.get("accounting", {}).get("auditor_reservations", {}).get("details"),

                    "accounting.change_accounting.flag": parse_flag(red_flags.get("accounting", {}).get("change_accounting", {}).get("flag")),
                    "accounting.change_accounting.details": red_flags.get("accounting", {}).get("change_accounting", {}).get("details"),

                    "accounting.adjustments.flag": parse_flag(red_flags.get("accounting", {}).get("adjustments", {}).get("flag")),
                    "accounting.adjustments.details": red_flags.get("accounting", {}).get("adjustments", {}).get("details"),

                    "accounting.tax_benefits.flag": parse_flag(red_flags.get("accounting", {}).get("tax_benefits", {}).get("flag")),
                    "accounting.tax_benefits.details": red_flags.get("accounting", {}).get("tax_benefits", {}).get("details"),

                    "accounting.tax_payments.flag": parse_flag(red_flags.get("accounting", {}).get("tax_payments", {}).get("flag")),
                    "accounting.tax_payments.details": red_flags.get("accounting", {}).get("tax_payments", {}).get("details"),

                    "accounting.no_audit.flag": parse_flag(red_flags.get("accounting", {}).get("no_audit", {}).get("flag")),
                    "accounting.no_audit.details": red_flags.get("accounting", {}).get("no_audit", {}).get("details"),

                    "accounting.conditional_outcomes.flag": parse_flag(red_flags.get("accounting", {}).get("conditional_outcomes", {}).get("flag")),
                    "accounting.conditional_outcomes.details": red_flags.get("accounting", {}).get("conditional_outcomes", {}).get("details"),

                    "liquidity.negative_wProfit.flag": parse_flag(red_flags.get("liquidity", {}).get("negative_wProfit", {}).get("flag")),
                    "liquidity.negative_wProfit.details": red_flags.get("liquidity", {}).get("negative_wProfit", {}).get("details"),

                    "liquidity.pensions.flag": parse_flag(red_flags.get("liquidity", {}).get("pensions", {}).get("flag")),
                    "liquidity.pensions.details": red_flags.get("liquidity", {}).get("pensions", {}).get("details"),

                    "delivery_date": red_flags.get("delivery_date"),
                    "mentioned_companies": red_flags.get("mentioned_companies"),
                    "mentioned_people": red_flags.get("mentioned_people"),
                    "auditor_name_redflag": red_flags.get("auditor_name")
                }))

            session.execute_write(neo4j.create_company, base_data)

            if base_data.get("ext_company_address"):
                session.execute_write(neo4j.create_address, base_data["id"], base_data["ext_company_address"])

            if base_data.get("company_address"):
                session.execute_write(neo4j.create_address, base_data["id"], base_data["company_address"])

            for entity in base_data.get("subsidiaries") or []:
                if isinstance(entity, str):
                    entity = [entity]
                for sub in entity:
                    if sub:
                        session.execute_write(
                            neo4j.create_relationship,
                            base_data["id"],
                            sub,
                            "PARENT_OF"
                        )

            parent = base_data.get("parent_company")
            if parent:
                session.execute_write(
                    neo4j.create_relationship,
                    base_data["id"],
                    parent,
                    "CHILD_OF"
                )

            for entity in base_data.get("ext_subsidiaries") or []:
                if isinstance(entity, str):
                    entity = [entity]
                for sub in entity:
                    if sub:
                        session.execute_write(
                            neo4j.create_relationship,
                            base_data["id"],
                            sub,
                            "PARENT_OF"
                        )

            parent_ext = base_data.get("ext_parent_company")
            if parent_ext:
                session.execute_write(
                    neo4j.create_relationship,
                    base_data["id"],
                    parent_ext,
                    "CHILD_OF"
                )

            for role in ("CEO", "board_members", "share_holders", "chairman_of_the_board"):
                people = base_data.get(f"leadership_{role}") or []
                if isinstance(people, str):
                    people = [people]
                for person in people:
                    if person:
                        session.execute_write(
                            neo4j.create_person_relationship,
                            person,
                            base_data["id"]
                        )

            for role in ("CEO", "board_members", "share_holders", "chairman_of_the_board"):
                people = base_data.get(f"ext_leadership_{role}") or []
                if isinstance(people, str):
                    people = [people]
                for person in people:
                    if person:
                        session.execute_write(
                            neo4j.create_person_relationship,
                            person,
                            base_data["id"]
                        )





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
