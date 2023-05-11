import networkx

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

csvs_dir = "/Users/meirinhos/Downloads/norsk/csvs/"
txts_dir = "/Users/meirinhos/Downloads/norsk/txts/"

csvs = list(filter(lambda x: x.endswith(".csv"), os.listdir(csvs_dir)))


lst = []

for i, csv in enumerate(csvs):
    if i % 100 == 0:
        print(i)

    df = pd.read_csv(csvs_dir + csv, keep_default_na=False)
    text = preprocess_text(extract_raw_text(df))

    with open(txts_dir + csv + ".txt", "w+") as f:
        f.writelines(text)

    table = extract_multi_column_text(text)[1]

    try:
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
        org_flag = any(map(text.__contains__, organisations.astype("str").stack()))
        red_flag = any(map(text.__contains__, redflags))

        lst.append(
            {"number": number, "name": name, "orgnums": org_flag, "redflags": red_flag}
        )
    except:
        pass


companies = pd.DataFrame(lst, columns=["number", "name", "orgnums", "redflags"])
companies.to_csv("companies.csv", index=False)
