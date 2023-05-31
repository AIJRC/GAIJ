import pandas as pd
import ast

from functools import reduce
import json

import networkx as nx
import matplotlib.pyplot as plt

df = pd.read_csv("companies-orgs.csv")
df["flagged_number"] = df["flagged_number"].apply(ast.literal_eval)
df["flagged_number"] = df["flagged_number"].apply(lambda x: x if len(x) > 0 else None)

mask = ~df["flagged_number"].isna()
df.loc[mask, "flags"] = df[mask].apply(lambda x: {int(y[0]) for y in x["flagged_number"]} - {x["number"]}, axis=1)
df.loc[mask, "flags"] = df.loc[mask, "flags"].apply(lambda x: set() if len(x) < 1 else x)
df.loc[~mask, "flags"] = df.loc[~mask, "flags"].apply(lambda x: set())

filtered_df = df[df["flags"].apply(len) > 0]
d = filtered_df.set_index("number")["flags"].to_dict()

graph = nx.Graph(d)

fig = plt.figure(figsize=(40, 40))
nx.draw(graph)
plt.show()

with open("../../downloads/enheter_alle.json") as file:
    data = json.load(file)
    data = {x["organisasjonsnummer"]: x for x in data}


def to_json():
    def find_name(key):
        if key in data.keys():
            return data[key]["navn"]
        else:
            return key

    def flatten_dict(d):
        flattened_list = []
        for key, value in d.items():
            if isinstance(value, set):
                for v in value:
                    flattened_list.append(
                        {
                            "source": find_name(str(key)),
                            "target": find_name(str(v)),
                            "value": 1,
                        }
                    )
            else:
                flattened_list.append(
                    {
                        "source": find_name(str(key)),
                        "target": find_name(str(value)),
                        "value": 1,
                    }
                )
        return flattened_list

    # Get all numbers that have connections to flagged companies
    numbers = set(df[df["flags"].apply(lambda x: x != set())]["number"].values)

    # Get all flagged companies
    flags = reduce(lambda x, y: x | y, df["flags"].values, set())

    # Get all nodes with names
    nodes = [{"id": find_name(str(x))} for x in numbers | flags]

    # Get all links
    links = flatten_dict(d)

    return {"nodes": nodes, "links": links}


with open("orgs.json", "w") as f:
    json.dump(to_json(), f, indent=4, sort_keys=True)
