import pandas as pd

import itertools

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from preprocessing import extract_raw_text, preprocess_text, extract_multi_column_text, find_substring_occurrences

redflags = [
    "Aksjonærlån",
    "Andre forhold",
    "Nedskrevet",
    "Tap/tapt",
    "konklusjon med forbehold",
    "negativ",
    "negativ konklusjon",
    "utfordringer med fortsatt drift",
    "usikkerhet vedrørende fortsatt drift",
    "konflikt",
    "handleplikt",
    "usikkerhet/usikkerheten",
    "skape tvil",
    "ulovlig",
    "ansvar for styret",
    "erstatningsansvar",
    "nderslag",
    "eversert",
    "ekstraordinært",
    "rstatning",
    "kattekrav",
    "nummerert brev",
    "søksmål/søksmålet",
    "presisering",
    "politianmeldt/politianmeldelse",
    "vesentlige mangler",
    "vesentlige mangler i intern kontroll",
    "mangelfull",
    "mangelfull intern kontroll",
]

# Red-flagged organisations
organisations = pd.read_csv("./orgnums.csv", dtype="Int64")

csvs_dir = "/home/francisco/files/csvs/"
txts_dir = "/home/francisco/files/txts/"

csvs = list(filter(lambda x: x.endswith(".csv"), os.listdir(csvs_dir)))

lst = []

for i, csv in enumerate(csvs):
    if i % 100 == 0:
        companies = pd.DataFrame(lst, columns=["number", "name", "orgnums", "redflags"])
        companies.to_csv("companies3.csv", index=False)
    try:
        df = pd.read_csv(csvs_dir + csv, keep_default_na=False)
        text = preprocess_text(extract_raw_text(df))

        with open(txts_dir + csv + ".txt", "w+") as f:
            f.writelines(text)

        table = extract_multi_column_text(text)[1]

        number = (
            table[table.iloc[:, 0] == "Organisasjonsnummer"]
            .dropna(axis=1)
            .iloc[:, 1]
            .values[0]
        )
        name = (
            table[table.iloc[:, 0] == "Foretaksnavn"]
            .dropna(axis=1)
            .iloc[:, 1]
            .values[0]
        )
        org_flag = itertools.chain.from_iterable(map(lambda x: find_substring_occurrences(text, x), organisations.astype('str').stack()))
        red_flag = itertools.chain.from_iterable(map(lambda x: find_substring_occurrences(text, x), redflags))
        lst.append({'number': number, 'name': name, 'orgnums': list(org_flag), 'redflags': list(red_flag)})
        # org_flag = any(map(text.__contains__, organisations.astype("str").stack()))
        # red_flag = any(map(text.__contains__, redflags))

    except:
        pass


companies = pd.DataFrame(lst, columns=["number", "name", "orgnums", "redflags"])
companies.to_csv("companies.csv", index=False)
