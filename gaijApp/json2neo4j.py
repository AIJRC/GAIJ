from neo4j import GraphDatabase
import json
import os
import argparse
import re
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

    def create_relationship(self, tx, from_id, to_name, to_type, rel_type,rel_kind):
        query = f"""
        MATCH (a:Company {{id: $from_id}})
        MERGE (b:{to_type} {{name: $to_name}})
        MERGE (a)-[r:{rel_type}]->(b)
        set r.kind = $rel_kind
        """
        return tx.run(query, from_id=from_id, to_name=to_name, rel_kind=rel_kind)


def load_markdown_notes(markdown_root):
    notes_by_id = {}
    for file in Path(markdown_root).rglob("*.md"):
        if len(file.relative_to(markdown_root).parts) > 2:
            continue  # Limit to 2 levels deep

        org_match = re.match(r'^(\d{9})', file.stem)
        if not org_match:
            continue
        org_id = org_match.group(1)
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()

        notes = {}
        for match in re.finditer(
            r'(Note\s+(\d+)\s*[-–]?\s*(.*?))\n(.{1,1000})(?=(?:\nNote\s+\d+\s*[-–]?|\Z))',
            content,
            re.DOTALL
        ):
            _, note_num, title, body = match.groups()
            body = body.strip()
            if len(body) > 1000:
                body = body[:1000].strip() + '...'  # Ensure 1000 characters and add ellipsis if needed
            notes[note_num] = f"{title.strip()}: {body}" if title else body

        notes_by_id[org_id] = notes
    return notes_by_id



def load_company_jsons(base_path):
    folders = ['external', 'llama', 'red_flags']
    # folders = ['external']
    # folders = ['red_flags']

    company_data = defaultdict(dict)

    for folder in folders:
        folder_path = os.path.join(base_path, folder)
        files = [f.name for f in Path(folder_path).glob('*.json')]
        # files = files[:5000]
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

def prepare_create_company_links(session, neo4j_connector, source_company_id, to_type, entity_names, relationship_label="",relationship_kind=""):
    entity_names = entity_names or []
    if isinstance(entity_names, str):
        entity_names = [entity_names]
    for entity_name in entity_names:
        if entity_name:
            session.execute_write(
                neo4j_connector.create_relationship,
                source_company_id,
                entity_name,
                to_type,
                relationship_label,
                relationship_kind
            )

def split_and_assign(parts):
        if len(parts) == 3:
            return {
                "day": parts[0],
                "month": parts[1],
                "year": parts[2]
            }
        return None

def extract_red_flag_data(red_flags_dict, company_id=None, note_lookup=None):
    """Helper function to extract structured data from the red_flags dictionary."""
    extracted_data = {}

    flag_categories = [
        ("finance", ["unclear_instruments", "hidden_leasing", "guarantee", "balance_values", "dependency"]),
        ("transactions", ["one_off_expense", "internal_transactions", "outstanding_receivables"]),
        ("accounting", ["auditor_reservations", "change_accounting", "adjustments", "tax_benefits", "tax_payments", "no_audit", "conditional_outcomes"]),
        ("liquidity", ["negative_wProfit", "pensions"])
    ]

    for category_key, sub_items in flag_categories:
        category_data = red_flags_dict.get(category_key, {})
        for sub_item_key in sub_items:
            sub_item_data = category_data.get(sub_item_key, {})
            extracted_data[f"{category_key}.{sub_item_key}.flag"] = parse_flag(sub_item_data.get("flag"))

            details = sub_item_data.get("details")
            if isinstance(details, str) and 'note' in details.lower():
                note_num_match = re.search(r'note\s*(\d+)', details.lower())
                if note_num_match and company_id and note_lookup:
                    note_num = note_num_match.group(1)
                    note_text = note_lookup.get(company_id, {}).get(note_num)
                    if note_text:
                        details += f" | {note_text}"

            extracted_data[f"{category_key}.{sub_item_key}.details"] = details

    # Handle direct mappings
    direct_mappings = {
        "mentioned_companies": "mentioned_companies",
        "mentioned_people": "mentioned_people",
        "auditor_name_redflag": "auditor_name" # target key in base_data : Source key in red_flags
    }
    for target_key, source_key in direct_mappings.items():
        extracted_data[target_key] = red_flags_dict.get(source_key)

    # handle flagged_words
    if "flagged_words" in red_flags_dict:
        try:
            flagged_words_data = red_flags_dict.get("flagged_words", {})
            extracted_data["flagged_words.flag"] = "true" 
            extracted_data["flagged_words.word"] = list(red_flags_dict["flagged_words"].keys()) 
            extracted_data["flagged_words.details"] = [red_flags_dict["flagged_words"][word]["sentence"] for word in  list(red_flags_dict["flagged_words"].keys())]
        except Exception as e: 
             print(f"Error parsing red flags '{flagged_words_data}': {e}. Skipping date parsing.")
             extracted_data["flagged_words.flag"] = "false"
    else:
        extracted_data["flagged_words.flag"] = "false"

    # Handle delivery_date
    delivery_date_str = red_flags_dict.get("delivery_date")
    # Case 1: string input with dots or dashes
    if delivery_date_str and isinstance(delivery_date_str, str):
        parsed = None
        for sep, order in [('.', 'DMY'), ('-', 'YMD')]:
            parts = delivery_date_str.split(sep)
            if len(parts) == 3:
                if order == 'YMD':
                    parts = [parts[2], parts[1], parts[0]]  # reorder
                    parsed = split_and_assign(parts)
                    extracted_data["delivery_date"] = parsed
                    break # Exit the loop once successfully parsed
                if order == 'DMY':
                    parsed = split_and_assign(parts)
                    extracted_data["delivery_date"] = parsed
                    break # Exit the loop once successfully parsed
        if not parsed:
            print(f"Warning: delivery_date '{delivery_date_str}' has an unexpected string format.")
    # Case 2: dict with 'details'    
    elif isinstance(delivery_date_str, dict) and 'details' in delivery_date_str:
        try: 
            parts = delivery_date_str['details'].split('.')
            parsed = split_and_assign(parts)
            if parsed:
                extracted_data["delivery_date"] = parsed
            else:
                print(f"Warning: delivery_date['details'] has unexpected format.")
                
        except Exception as e: 
            print(f"Error parsing delivery_date '{delivery_date_str}': {e}. Skipping date parsing.")
       
        
        """
        try:
            parts = delivery_date_str.split('.') 
            if len(parts) == 3:
                extracted_data["delivery_date.day"] = parts[0] 
                extracted_data["delivery_date.month"] = parts[1]
                extracted_data["delivery_date.year"] = parts[2]
            else:
                try: 
                    parts = delivery_date_str.split('-') 
                    if len(parts) == 3:
                        extracted_data["delivery_date.day"] = parts[2] 
                        extracted_data["delivery_date.month"] = parts[1]
                        extracted_data["delivery_date.year"] = parts[0]
                    else:
                        try: 
                            parts = delivery_date_str['details'].split('.') 
                            if len(parts) == 3:
                                extracted_data["delivery_date.day"] = parts[0] 
                                extracted_data["delivery_date.month"] = parts[1]
                                extracted_data["delivery_date.year"] = parts[2]
                            else:
                                print(f"Warning: delivery_date '{delivery_date_str}' has unexpected format. Skipping date parsing.")
                        except Exception as e: #
                            print(f"Error parsing delivery_date '{delivery_date_str}': {e}. Skipping date parsing.")
                except Exception as e: #
                    print(f"Error parsing delivery_date '{delivery_date_str}': {e}. Skipping date parsing.")
        except Exception as e: #
            print(f"Error parsing delivery_date '{delivery_date_str}': {e}. Skipping date parsing.")
    elif delivery_date_str: # If it exists but isn't a string, or if parsing failed earlier
        print(f"Warning: delivery_date '{delivery_date_str}' is not a string or has an issue. Skipping date parsing.")
"""
    return extracted_data


def populate_graph_from_directory(directory_path, neo4j, note_lookup):
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
                
                def build_ext_leadership(leadership):
                    roles = ["CEO", "board_members", "share_holders", "chairman_of_the_board"]
                    people = []
                    for role in roles:
                        val = leadership.get(role)
                        if val is None or val == "null":
                            continue
                        if isinstance(val, list):
                            people.extend([p for p in val if p and p != "null" and p != ["null"]])
                        else:
                            if val != "null":
                                people.append(val)
                    # Remove any accidental ['null'] entries
                    people = [p for p in people if p and p != "null" and p != ["null"]]
                    return people

                # ext_leadership = build_ext_leadership(external.get("leadership", {}))
                base_data.update(flatten_keys({
                    "ext_company_name": external.get("company_name"),
                    "name": external.get("company_name"),
                    "ext_company_address": external.get("company_address"),
                    "ext_company_type": external.get("company_type"),
                    "ext_leadership": external.get("leadership", []),
                    "ext_subsidiaries": external.get("subsidiaries"),
                    "ext_parent_company": external.get("parent_company"),
                    "ext_auditor_name": external.get("auditor_name"),
                }))
            
            if llama:
                base_data.update(flatten_keys({
                    "name": llama.get("name"),
                    "company_address": llama.get("address"),
                    "company_type": llama.get("type"),
                    "leadership": llama.get("leadership", {}).get("names", {}),
                    "subsidiaries": llama.get("subsidiaries"),
                    "parent_company": llama.get("parent"),
                    "auditor_name": llama.get("auditor"),
                    "version_control": llama.get("version_control"),
                }))
            
            if red_flags:
                extracted_rf_data = extract_red_flag_data(red_flags, company_id, note_lookup)
                base_data.update(flatten_keys(extracted_rf_data))

            session.execute_write(neo4j.create_company, base_data)

            prepare_create_company_links(session, neo4j, base_data["id"], "Address", base_data.get("ext_company_address", []), "LOCATED_AT_ext","located_at")
            prepare_create_company_links(session, neo4j, base_data["id"], "Address", base_data.get("company_address", []), "LOCATED_AT_llm","located_at")
            
            prepare_create_company_links(session, neo4j, base_data["id"], "Company", base_data.get("subsidiaries", []), "PARENT_OF_llm","parent_of")
            prepare_create_company_links(session, neo4j, base_data["id"], "Company", base_data.get("parent_company", []), "CHILD_OF_llm","child_of")
            prepare_create_company_links(session, neo4j, base_data["id"], "Company", base_data.get("mentioned_companies", []), "mentioned","mentioned")
            prepare_create_company_links(session, neo4j, base_data["id"], "Company", base_data.get("ext_subsidiaries", []), "PARENT_OF_ext","parent_of")
            prepare_create_company_links(session, neo4j, base_data["id"], "Company", base_data.get("ext_parent_company", []), "CHILD_OF_ext","child_of")

            prepare_create_company_links(session, neo4j, base_data["id"], "Person", base_data.get(f"leadership", []), "LED_BY_llm","led_by")
            prepare_create_company_links(session, neo4j, base_data["id"], "Person", base_data.get(f"ext_leadership", []), "LED_BY_ext","led_by")

            prepare_create_company_links(session, neo4j, base_data["id"], "Person", base_data.get("mentioned_people", []), "mentioned_llm","mentioned")
            prepare_create_company_links(session, neo4j, base_data["id"], "Auditor", base_data.get("auditor_name_redflag", []), "auditor_llm","auditor")
            prepare_create_company_links(session, neo4j, base_data["id"], "Auditor", base_data.get("ext_auditor_name", []), "auditor_ext","auditor")


def main():
    args = parse_args()
    neo4j = Neo4jConnector()
    try:
        markdown_notes = load_markdown_notes(os.path.expanduser('~/data/markdowns'))
        populate_graph_from_directory(args.data_dir, neo4j, markdown_notes)
        print("Knowledge graph populated successfully!")
    finally:
        neo4j.close()

if __name__ == "__main__":
    main()
