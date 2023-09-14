import pandas as pd
import json

from collections import Counter

import networkx as nx

from itertools import chain

DATA_DIR = "../../data/"

initial_suspects = set(pd.read_csv("./suspects.csv", dtype="Int64").stack())

df = pd.read_json("../../data/companies-new.json", orient='records', lines=True)

def get_data(df):
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
            "number": row["number"],
            "suspect": int(row["number"]) in initial_suspects
        }
        nodes.append(node_data)

    # Add nodes that are not in df
    missing_nodes = unique_nodes - set(df_filtered["name"].values)
    for node in missing_nodes:
        nodes.append({"id": node, "number": node, "industry_name": "Unknown", "suspect": int(node) in initial_suspects})

    
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


def find_subgraphs(data, output_directory="."):
    """
    Finds and exports separate subgraphs from a given JSON structure.

    Parameters:
    - data (dict): A dictionary containing nodes and links representing a graph.
    - output_directory (str): Directory where the subgraph JSON files will be saved.

    Returns:
    - List of paths to the generated JSON files.
    """

    # Create a graph from the JSON data using NetworkX
    G = nx.DiGraph()
    for node in data['nodes']:
        G.add_node(node['id'], **node)
    for link in data['links']:
        G.add_edge(link['source'], link['target'], **link)

    # Extract connected components (subgraphs)
    subgraphs = [G.subgraph(c) for c in nx.weakly_connected_components(G)]

    # Only care about subgraphs which are connected to the initial suspects
    subgraphs = filter(lambda g: any(node in initial_suspects for node in g.nodes()), subgraphs)

    # Convert each subgraph back to the JSON format
    subgraph_data = []
    for subgraph in subgraphs:
        nodes = [{"id": node, **subgraph.nodes[node]} for node in subgraph.nodes]
        links = [{"source": edge[0], "target": edge[1], **subgraph.edges[edge]} for edge in subgraph.edges]
        
        # Calculate number of nodes in the subgraph
        num_nodes = len(nodes)
        
        # Determine industry of the subgraph
        industries = [node["industry_name"] for node in nodes if "industry_name" in node and node["industry_name"] is not None]
        if len(industries) == 0:
            industry = "Unknown"
        else:
            # Check top 3 industries
            industry_counts = Counter(industries)
            top_3_industries = [industry[0] for industry in industry_counts.most_common(3)]
            industry = ", ".join(top_3_industries)
        
        subgraph_data.append({
            "nodes": nodes, 
            "links": links,
            "num_nodes": num_nodes,
            "industry": industry
        })

    return sorted(subgraph_data, key=lambda x: x['num_nodes'], reverse=True)

def generate_subgraph_list_json(subgraphs, output_directory="."):
    """
    Generates a list of subgraphs with their paths, industries, and number of nodes.
    This list is saved as a JSON file.
    """
    subgraph_list = []
    for idx, subgraph in enumerate(subgraphs, 1):
        subgraph_data = {
            "path": f"subgraphs/graph_{idx}.json",
            "industry": subgraph["industry"],
            "num_nodes": subgraph["num_nodes"]
        }
        subgraph_list.append(subgraph_data)

    list_filename = output_directory + "subgraphs_list.json"
    with open(list_filename, "w") as f:
        json.dump(subgraph_list, f, indent=4, sort_keys=True)

    return list_filename

data = get_data(df)

with open(DATA_DIR + "orgs.json", "w") as f:
    json.dump(data, f, indent=4, sort_keys=True)

subgraph_data = find_subgraphs(data)

for idx, subgraph in enumerate(subgraph_data, 1):
    with open(DATA_DIR + f"/subgraphs/graph_{idx}.json", "w") as f:
        json.dump(subgraph, f, indent=4, sort_keys=True)

generate_subgraph_list_json(subgraph_data, DATA_DIR)
