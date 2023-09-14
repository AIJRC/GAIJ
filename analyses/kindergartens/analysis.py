import pandas as pd
import json

import networkx as nx
from networkx.algorithms import community

from itertools import chain

DATA_DIR = "../../data"

initial_suspects = set(pd.read_csv("./suspects.csv", dtype="Int64").stack())

df = pd.read_json(f"{DATA_DIR}/companies-new.json", orient='records', lines=True)

def get_unique_graphs(graph_list):
    unique_graphs = []

    for graph in graph_list:
        is_unique = True
        for unique_graph in unique_graphs:
            if nx.is_isomorphic(graph, unique_graph):
                is_unique = False
                break
        if is_unique:
            unique_graphs.append(graph)

    return unique_graphs

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

    k = 3

    all_k_communities = []

    for g in subgraphs:
        if g.number_of_nodes() > 20:
            g = g.to_undirected()

            communities = list(community.label_propagation_communities(g))
            all_k_communities.extend(communities)
            communities = list(community.k_clique_communities(g, k + 1))
            all_k_communities.extend(communities)
            communities = list(community.k_clique_communities(g, k))
            all_k_communities.extend(communities)
            communities = list(community.asyn_fluidc(g, k + 2))
            all_k_communities.extend(communities)
            communities = list(community.asyn_fluidc(g, k + 1))
            all_k_communities.extend(communities)
            communities = list(community.asyn_fluidc(g, k))
            all_k_communities.extend(communities)


    for community_set in all_k_communities:
        subgraph = G.subgraph(community_set)
        subgraphs.append(subgraph)

    # Only care about subgraphs which are connected to the initial suspects
    subgraphs = filter(lambda g: any(node in initial_suspects for node in g.nodes()), subgraphs)

    subgraphs = get_unique_graphs(subgraphs)

    # Convert each subgraph back to the JSON format
    subgraph_data = []
    for subgraph in subgraphs:
        nodes = [{"id": node, **subgraph.nodes[node]} for node in subgraph.nodes]
        links = [{"source": edge[0], "target": edge[1], **subgraph.edges[edge]} for edge in subgraph.edges]
        
        # Determine top suspects of the subgraph
        suspects_in_subgraph = [node for node in initial_suspects if node in subgraph.nodes()]
        sorted_suspects = sorted(suspects_in_subgraph, key=lambda n: subgraph.degree(n), reverse=True)
        top_suspects = [subgraph.nodes[suspect]['id'] for suspect in sorted_suspects[:3]]

        subgraph_data.append({
            "nodes": nodes,
            "links": links,
            "num_nodes": len(nodes),
            "top_suspects": ", ".join(str(suspect) for suspect in top_suspects)
        })

    return sorted(subgraph_data, key=lambda x: x['num_nodes'], reverse=True)

data = get_data(df)

with open(f"{DATA_DIR}/orgs.json", "w") as f:
    json.dump(data, f, indent=4, sort_keys=True)

subgraph_data = find_subgraphs(data)
subgraph_list = []
for idx, subgraph in enumerate(subgraph_data, 1):
    subgraph_data = {
        "path": f"{DATA_DIR}/subgraphs/graph_{idx}.json",
        "top_suspects": subgraph["top_suspects"],
        "num_nodes": subgraph["num_nodes"]
    }
    subgraph_list.append(subgraph_data)

    with open(f"{DATA_DIR}/subgraphs/graph_{idx}.json", "w") as f:
        json.dump(subgraph, f, indent=4, sort_keys=True)
    
with open(f"{DATA_DIR}/subgraphs_list.json", "w") as f:
    json.dump(subgraph_list, f, indent=4, sort_keys=True)
