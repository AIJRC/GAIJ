import pandas as pd
import re
import json

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from preprocessing import extract_raw_text, preprocess_text, extract_multi_column_text


def find_dictionary(dicts, key, value):
    for d in dicts:
        if d.get(key) == value:
            return d


def find_row_with_value(df, value):
    mask = df.eq(value).any(axis=1)
    return df[mask].iloc[0] if any(mask) else None


csvs_dir = "../../downloads/csvs/"
txts_dir = "../../downloads/txts/"

ocred = set(filter(lambda x: x.endswith(".csv"), os.listdir(csvs_dir)))

lst = []

for i, csv in enumerate(ocred):
    try:
        df = pd.read_csv(csvs_dir + csv, keep_default_na=False)
        text = preprocess_text(extract_raw_text(df))

        with open(txts_dir + csv + ".txt", "w+") as f:
            f.writelines(text)

        table = extract_multi_column_text(text)[1]

        number = find_row_with_value(table, "Organisasjonsnummer").dropna().values[1]
        name = find_row_with_value(table, "Foretaksnavn").dropna().values[1]

        lst.append({'number': int(number), 'name': name})

    except:
        pass


df = pd.DataFrame(lst, columns=["number", "name"])
df.to_csv("companies.csv", index=False)

# Open alternative file with names (navn) and numbers (organisasjonsnummer)
with open("../../downloads/enheter_alle.json") as file:
    data = json.load(file)
    data = {x["organisasjonsnummer"]: x for x in data}

df = pd.read_csv("companies.csv").fillna(0).astype({"number": int})

missing_number = df[df["number"] == 0]

for i, row in missing_number.iterrows():
    d = find_dictionary(data, "navn", str(row["name"]))
    if d is not None:
        df.loc[i, "number"] = d["organisasjonsnummer"]

missing_name = df[df["name"] == 0]

for i, row in missing_name.iterrows():
    d = find_dictionary(data, "organisasjonsnummer", str(row["number"]))
    if d is not None:
        df.loc[i, "name"] = d["navn"]

# Ensure there are no companies that cannot be identified
df = df[(df["name"] != 0) & (df["number"] != 0)]

# Get "alternative" (most likely the correct name) name for
for i, row in df.iterrows():
    number = str(row["number"])
    if number in data:
        name = data[number]["navn"]
        df.loc[i, "name-alt"] = name if row["name"] != name else None

# Replace all whitespaces by a single whitespace
df["name"] = df["name"].apply(lambda x: re.sub(r"\s+", " ", x))
df["name-alt"] = df["name-alt"].apply(lambda x: re.sub(r"\s+", " ", x) if not pd.isnull(x) else x)

df.to_csv("companies.csv", index=False)
