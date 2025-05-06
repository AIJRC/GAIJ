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
        print(query)
        # return tx.run(query, **props)
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


def load_company_jsons(base_path):
    folders = ['external', 'llama', 'red_flags']
    company_data = defaultdict(dict)

    for folder in folders:
        folder_path = os.path.join(base_path, folder)
        files = [f.name for f in Path(folder_path).glob('*.json')]
        files = files[:10]
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

def populate_graph_from_directory(directory_path, neo4j):
    companies_data = load_company_jsons(directory_path)

    with neo4j.driver.session() as session:
        for company_id, data_sources in tqdm(companies_data.items(), desc="Processing companies"):
            external = data_sources.get("external", {})
            # print(external)
            llama = data_sources.get("llama", {})
            red_flags = data_sources.get("red_flags", {})
            # print(red_flags)

            if not external.get("company_id") and not llama.get("ID"):
                continue

            base_data = {"ID": company_id}

            if external:
                base_data.update({
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
                })
            
            if llama:
                base_data.update({
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
                })
            
            if red_flags:
                base_data.update({
                    "finance.unclear_instruments.flag": bool(red_flags.get("finance", {}).get("unclear_instruments")),
                    "finance.unclear_instruments.details": red_flags.get("finance", {}).get("unclear_instruments"),
                    "finance.hidden_leasing.flag": bool(red_flags.get("finance", {}).get("hidden_leasing")),
                    "finance.hidden_leasing.details": red_flags.get("finance", {}).get("hidden_leasing"),
                    "finance.guarantee.flag": bool(red_flags.get("finance", {}).get("guarantee")),
                    "finance.guarantee.details": red_flags.get("finance", {}).get("guarantee"),
                    "finance.balance_values.flag": bool(red_flags.get("finance", {}).get("balance_values")),
                    "finance.balance_values.details": red_flags.get("finance", {}).get("balance_values"),
                    "finance.dependency.flag": bool(red_flags.get("finance", {}).get("dependency")),
                    "finance.dependency.details": red_flags.get("finance", {}).get("dependency"),

                    "transactions.one_off_expense.flag": bool(red_flags.get("transactions", {}).get("one_off_expense")),
                    "transactions.one_off_expense.details": red_flags.get("transactions", {}).get("one_off_expense"),
                    "transactions.internal_transactions.flag": bool(red_flags.get("transactions", {}).get("internal_transactions")),
                    "transactions.internal_transactions.details": red_flags.get("transactions", {}).get("internal_transactions"),
                    "transactions.outstanding_receivables.flag": bool(red_flags.get("transactions", {}).get("outstanding_receivables")),
                    "transactions.outstanding_receivables.details": red_flags.get("transactions", {}).get("outstanding_receivables"),

                    "accounting.auditor_reservations.flag": bool(red_flags.get("accounting", {}).get("auditor_reservations")),
                    "accounting.auditor_reservations.details": red_flags.get("accounting", {}).get("auditor_reservations"),
                    "accounting.change_accounting.flag": bool(red_flags.get("accounting", {}).get("change_accounting")),
                    "accounting.change_accounting.details": red_flags.get("accounting", {}).get("change_accounting"),
                    "accounting.adjustments.flag": bool(red_flags.get("accounting", {}).get("adjustments")),
                    "accounting.adjustments.details": red_flags.get("accounting", {}).get("adjustments"),
                    "accounting.tax_benefits.flag": bool(red_flags.get("accounting", {}).get("tax_benefits")),
                    "accounting.tax_benefits.details": red_flags.get("accounting", {}).get("tax_benefits"),
                    "accounting.tax_payments.flag": bool(red_flags.get("accounting", {}).get("tax_payments")),
                    "accounting.tax_payments.details": red_flags.get("accounting", {}).get("tax_payments"),
                    "accounting.no_audit.flag": bool(red_flags.get("accounting", {}).get("no_audit")),
                    "accounting.no_audit.details": red_flags.get("accounting", {}).get("no_audit"),
                    "accounting.conditional_outcomes.flag": bool(red_flags.get("accounting", {}).get("conditional_outcomes")),
                    "accounting.conditional_outcomes.details": red_flags.get("accounting", {}).get("conditional_outcomes"),

                    "liquidity.negative_wProfit.flag": bool(red_flags.get("liquidity", {}).get("negative_wProfit")),
                    "liquidity.negative_wProfit.details": red_flags.get("liquidity", {}).get("negative_wProfit"),
                    "liquidity.pensions.flag": bool(red_flags.get("liquidity", {}).get("pensions")),
                    "liquidity.pensions.details": red_flags.get("liquidity", {}).get("pensions"),

                    "delivery_date": red_flags.get("delivery_date"),
                    "mentioned_companies": red_flags.get("mentioned_companies"),
                    "mentioned_people": red_flags.get("mentioned_people"),
                    "auditor_name_redflag": red_flags.get("auditor_name")
                })
            # print(base_data)
            session.execute_write(neo4j.create_company, base_data)
            break
            # if base_data["ext.company_address"]:
            #     session.execute_write(neo4j.create_address, base_data["ID"], base_data["ext.company_address"])

            # if base_data["company_address"]:
            #     session.execute_write(neo4j.create_address, base_data["ID"], base_data["company_address"])

            # for entity in base_data.get("subsidiaries") or []:
            #     if isinstance(entity, str):
            #         entity = [entity]
            #     for sub in entity:
            #         if sub:
            #             session.execute_write(
            #                 neo4j.create_relationship,
            #                 base_data["ID"],
            #                 sub,
            #                 "PARENT_OF"
            #             )

            # parent = base_data.get("parent_company")
            # if parent:
            #     session.execute_write(
            #         neo4j.create_relationship,
            #         base_data["ID"],
            #         parent,
            #         "CHILD_OF"
            #     )

            # for role in ("CEO", "board_members", "share_holders", "chairman_of_the_board"):
            #     people = base_data.get(f"leadership.{role}") or []
            #     if isinstance(people, str):
            #         people = [people]
            #     for person in people:
            #         if person:
            #             session.execute_write(
            #                 neo4j.create_person_relationship,
            #                 person,
            #                 base_data["ID"]
            #             )

            # for role in ("CEO", "board_members", "share_holders", "chairman_of_the_board"):
            #     people = base_data.get(f"ext.leadership.{role}") or []
            #     if isinstance(people, str):
            #         people = [people]
            #     for person in people:
            #         if person:
            #             session.execute_write(
            #                 neo4j.create_person_relationship,
            #                 person,
            #                 base_data["ID"]
            #             )

            # for entity in base_data.get("ext.subsidiaries") or []:
            #     if isinstance(entity, str):
            #         entity = [entity]
            #     for sub in entity:
            #         if sub:
            #             session.execute_write(
            #                 neo4j.create_relationship,
            #                 base_data["ID"],
            #                 sub,
            #                 "PARENT_OF"
            #             )

            # parent_ext = base_data.get("ext.parent_company")
            # if parent_ext:
            #     session.execute_write(
            #         neo4j.create_relationship,
            #         base_data["ID"],
            #         parent_ext,
            #         "CHILD_OF"
            #     )



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
