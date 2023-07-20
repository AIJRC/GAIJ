import pandas as pd
import json

from itertools import chain

df = pd.read_json("../../data/companies-new.json", orient='records', lines=True)

def to_json(df):
    number_to_name = df.set_index('number')['name'].to_dict()
    
    # Filter for relevant rows
    flagged_df = df[df["flagged_names"].astype(bool) | df["flagged_numbers"].astype(bool)]
    
    # Extract node IDs
    name_nodes = flagged_df['name'].tolist()
    flagged_name_nodes = [node for sublist in flagged_df["flagged_names"].dropna() for node in sublist]
    flagged_number_nodes = [number_to_name.get(num, num) for sublist in flagged_df["flagged_numbers"].dropna() for num in sublist]
    unique_nodes = set(name_nodes + flagged_name_nodes + flagged_number_nodes)

    # Filter dataframe for unique nodes
    df_filtered = df[df["name"].isin(unique_nodes)]
    
    nodes = []
    for _, row in df_filtered.iterrows():
        node_data = {
            "id": row["name"],
            "industry_name": row["industry_name"],
            "number": row["number"]
        }
        nodes.append(node_data)

    # Add nodes that are not in df
    missing_nodes = unique_nodes - set(df_filtered["name"].values)
    for node in missing_nodes:
        nodes.append({"id": node})

    
    # Generate links without relying on unique indexing
    links = []
    for _, row in flagged_df.iterrows():
        name = row['name']
        links.extend(create_links(name, row.get("flagged_names", {}), False, number_to_name))
        links.extend(create_links(name, row.get("flagged_numbers", {}), True, number_to_name))
    
    # Remove duplicate links
    unique_links = list({(link['source'], link['target']): link for link in links}.values())
    
    return {"nodes": nodes, "links": unique_links}


def create_links(source, targets, is_number, num_to_name_mapping):
    if isinstance(targets, (list, set)):
        targets = set(targets)
    else:
        targets = {targets}

    return [{"source": source, 
             "target": (num_to_name_mapping.get(target, target) if is_number else target),
             "value": 1} for target in targets]


with open("../../data/orgs.json", "w") as f:
    json.dump(to_json(df), f, indent=4, sort_keys=True)
