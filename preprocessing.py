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


def process_text(text):
    # Replaces "O" by "0" if they are the beginning, middle or end of digits
    text = re.sub(r"(?<=\d)O(?=\d)|(?<=\d)O|O(?=\d)", "0", text)

    # Removes single or double whitespaces between numbers "1 000" becomes "1000"
    text = re.sub("(?<=\d) {1,2}(?=\d)", "", text)

    return text


if __name__ == "__main__":
    NUM_THREADS = 6

    # Find all .csv files
    csvs = list(filter(lambda x: x.endswith(".csv"), os.listdir("./csvs/")))

    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:

        def procedure(csv_name):
            try:
                df = pd.read_csv("./csvs/" + csv_name, keep_default_na=False)
                text = extract_raw_text(df)
                text = process_text(text)

            except Exception as e:
                logging.warning("Failed with {}".format(csv_name), e)

        out = executor.map(procedure, csvs)
