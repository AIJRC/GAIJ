import pandas as pd
import re
import json

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils import extract_raw_text, preprocess_text, extract_multi_column_text

CSV_DIR = "../../data/csvs/"
TXT_DIR = "../../data/txts/"
DATA_JSON = "../../data/enheter_alle.json"
OUTPUT_CSV = "../../data/companies.csv"


def find_row_with_value(df, value):
    mask = df.eq(value).any(axis=1)
    return df[mask].iloc[0] if any(mask) else None


data = []

for csv_file in filter(lambda x: x.endswith(".csv"), os.listdir(CSV_DIR)):
    try:
        df = pd.read_csv(CSV_DIR + csv_file, keep_default_na=False)
        text = preprocess_text(extract_raw_text(df))
        with open(TXT_DIR + csv_file + ".txt", "w+") as file:
            file.writelines(text)
        table = extract_multi_column_text(text)[1]
        number = find_row_with_value(table, "Organisasjonsnummer").dropna().values[1]
        name = find_row_with_value(table, "Foretaksnavn").dropna().values[1]
        data.append({'number': int(number), 'name': name})

    except:
        pass

df = pd.DataFrame(data, columns=["number", "name"])

with open(DATA_JSON) as file:
    json_data = {item["organisasjonsnummer"]: item for item in json.load(file)}

def resolve_missing(row):
    if row["number"] == 0:
        found = json_data.get(row["name"])
        if found:
            row["number"] = int(found["organisasjonsnummer"])
            row["name"] = found["navn"]
    elif row["name"] == 0:
        found = json_data.get(str(row["number"]))
        if found:
            row["name"] = found["navn"]
    return row

df = df.apply(resolve_missing, axis=1)
df = df[(df["name"] != 0) & (df["number"] != 0)]
df["name-alt"] = df["number"].map(lambda x: None if json_data.get(str(x), {}).get("navn") == df.loc[x, "name"] else json_data.get(str(x), {}).get("navn"))
df["name"] = df["name"].str.replace(r"\s+", " ")
df["name-alt"] = df["name-alt"].str.replace(r"\s+", " ")

df.to_csv(OUTPUT_CSV, index=False)
