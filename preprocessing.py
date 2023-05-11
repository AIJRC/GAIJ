import pandas as pd
import re

import concurrent.futures

import os


def extract_raw_text(df):
    # split into pages
    def slice_pages(df):
        idx = df.index[df["level"] == 1].tolist()
        sliced_list = [df[idx[i] : idx[i + 1]] for i in range(len(idx) - 1)]
        sliced_list.append(df[idx[-1] :])
        return sliced_list

    dfs = slice_pages(df)

    full_text = ""

    for df in dfs:
        # Only level `5` contains text
        text = df[(df["level"] == 5) & (df["text"] != "") & (df.text != " ")]
        text = text.astype({"text": "str"})

        # Estimate the size of a char in the current page (probably average of the mode would be more accurate)
        char_w = (text["width"] / text["text"].str.len()).mean()

        assert df[df["block_num"] > 1].empty

        # NOTE: rework on this later
        # See https://stackoverflow.com/a/59666326
        # par_num and line_num control both the vertical alignment whereas left controls the left anchor position of the detected box
        prev_par, prev_line, prev_left = 0, 0, 0
        for _, ln in df.iterrows():
            # add new line when necessary
            if prev_par != ln["par_num"]:
                prev_par = ln["par_num"]
                prev_line = ln["line_num"]
                prev_left = 0
                full_text += "\n"
            elif prev_line != ln["line_num"]:
                prev_line = ln["line_num"]
                prev_left = 0
                full_text += "\n"

            added = 0  # num of spaces that should be added
            if ln["left"] // char_w > prev_left + 1:
                added = int(ln["left"] // char_w) - prev_left
                full_text += " " * added
            full_text += ln["text"] + " "
            prev_left += len(ln["text"]) + added + 1
        full_text += "\n"

    return full_text


def preprocess_text(text, tab_width=8):
    # Replaces "O" by "0" if they are the beginning, middle or end of digits
    text = re.sub(r"(?<=\d)O(?=\d)|(?<=\d)O|O(?=\d)", "0", text)

    # Removes single or double whitespaces between numbers "1 000" becomes "1000"
    text = re.sub("(?<=\d) {1,2}(?=\d)", "", text)

    # Replace consecutive whitespaces with tabs
    text = re.sub(r" {2,}", lambda m: "\t" * (len(m.group()) // tab_width) + " " * (len(m.group()) % tab_width), text)

    # Remove left trailing whitespace (either ' ' or '\t')
    text = re.sub(r"^[ \t]+", "", text, flags=re.MULTILINE)

    return text


def extract_multi_column_text(text):
    blocks = []
    tables = []
    matches = re.finditer(r"(^|\n)(\s*.*?)(?=\n|\Z)", text, flags=re.DOTALL)
    for match in matches:
        block = match.group(2)
        cells = [line.split("\t") for line in block.split("\n")]
        num_columns = max(len(row) for row in cells)
        if num_columns <= 1:
            blocks.append(block)
        else:
            data = [row for row in cells if len(row) == num_columns][0]
            tables.append(data)

    tables = pd.DataFrame(tables)

    # Remove trailing whitespaces and colons on all elements
    tables = tables.applymap(lambda x: re.sub(r"\s*[:\s]*\s*$", "", str(x)))

    # Remove trailing whitespaces on cells with digits
    #     df = df.applymap(lambda x: re.sub(r"^\s+|\s+$"", "", x) if re.search(r'\d', x) else x)
    tables = tables.applymap(lambda x: re.sub(r"^\s+|\s+$", "", x))

    # Changes empty strings to None
    tables = tables.replace(r"^\s*$", None, regex=True)

    return blocks, tables


if __name__ == "__main__":
    NUM_THREADS = 6

    # Find all .csv files
    csvs = list(filter(lambda x: x.endswith(".csv"), os.listdir("./csvs/")))

    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:

        def procedure(csv_name):
            try:
                df = pd.read_csv("./csvs/" + csv_name, keep_default_na=False)
                text = extract_raw_text(df)
                text = preprocess_text(text)
                text = extract_multi_column_text(text)

            except Exception as e:
                logging.warning("Failed with {}".format(csv_name), e)

        out = executor.map(procedure, csvs)
