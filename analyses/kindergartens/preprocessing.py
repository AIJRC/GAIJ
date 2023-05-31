import pandas as pd
import re

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from preprocessing import find_substring_occurrences


df = pd.read_csv("companies.csv").astype({"number": int})

# Red-flagged organisations
redflagged_numbers = set(pd.read_csv("./orgnums.csv", dtype="Int64").stack().values)

df["flagged_number"] = [[]] * len(df)

all_suspects = redflagged_numbers
current_suspects = all_suspects

while len(current_suspects) > 0:

    for i, row in df.iterrows():

        with open(f"../../downloads/txts/{str(row['number'])}_arso_2020.csv.txt", "r") as f:
            text = f.read()

        matches = [m for s in current_suspects for m in find_substring_occurrences(str(s), text)]

        df.at[i, "flagged_number"] = df.at[i, "flagged_number"] + matches

    # Find all companies with connections to the current suspects
    mask = df["flagged_number"].apply(lambda x: x != [])
    new_suspects = set(df[mask]["number"].values)

    # Update suspects
    current_suspects = new_suspects - all_suspects
    all_suspects = all_suspects | new_suspects

# Red-flagged words
redflags = pd.read_csv("./redflags.csv").astype("str")
