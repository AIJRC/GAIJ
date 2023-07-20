import pandas as pd
import re
import json

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from preprocessing import find_9_digit_words

df = pd.read_csv("../../data/companies.csv").astype({"number": int})

# Load data from JSON file
with open("../../data/enheter_alle.json", "r") as f:
    df_json = pd.json_normalize(json.load(f))

# Prepare industry mapping
identifier = "naeringskode1"
industry_mapping = df_json.set_index(f"{identifier}.kode")[f"{identifier}.beskrivelse"].to_dict()

# Add industry name to the companies' dataframe
df = pd.read_json("../../data/companies-names.json", orient='records', lines=True)
df['industry_name'] = df['number'].astype(str).map(df_json.set_index('organisasjonsnummer')['naeringskode1.kode'].map(industry_mapping))

# Finds all possible connections with other companies, by number
# It is much cheaper to simply match 9-number words
df['flagged_numbers'] = None
for i, row in df.iterrows():

    with open(f"../../data/txts/{str(row['number'])}_arso_2020.csv.txt", "r") as f:
        text = f.read()

    df.at[i, "flagged_numbers"] = [int(m) for m in find_9_digit_words(text) if len(str(int(m))) == 9]

# Find all suspects having connections to `suspects.csv` by number
all_suspects = set(pd.read_csv("./suspects.csv", dtype="Int64").stack())

# False-positive suspects
no_suspects = {123456789, 999999999} 

current_suspects = all_suspects - no_suspects

# Identify suspects by number
while current_suspects:
    
    # Find all companies with references to the current suspects
    mask = df["flagged_numbers"].apply(lambda x: bool(set(x) & current_suspects))

    # Said companies are also now possible suspects
    new_suspects = set(df[mask]["number"])

    # Update suspects
    current_suspects = new_suspects - all_suspects - no_suspects
    all_suspects |= new_suspects

# Cleanup operation
df.loc[df["flagged_numbers"].notna(), "flagged_numbers"] = df.loc[df["flagged_numbers"].notna()].apply(lambda x: (set(x["flagged_numbers"]) & all_suspects) - no_suspects - {x["number"]}, axis = 1)
# df.loc[df["flagged_names"].notna(), "flagged_names"] = df.loc[df["flagged_names"].notna(), "flagged_names"].apply(set)
# df.loc[df["flagged_names"].notna(), "flagged_names"] = df.loc[df["flagged_names"].notna()].apply(lambda x: set(x["flagged_names"]) - {x["name"]}, axis = 1)

df.to_json("../../data/database.json", orient = 'records', lines = True)