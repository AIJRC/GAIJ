import re


def preprocess_tsv(tsv, inner_delimiter="\t", outer_delimiter="\n"):
    # Convert the TSV string to a list of rows
    rows = [row.split(inner_delimiter) for row in tsv.strip().split(outer_delimiter)]

    # Each row has the following elements
    # level, page_num, block_num, par_num, line_num, word_num, left, top, width, height, conf, text
    # Ignore rows with *negative* `conf`idence level or empty text
    out = filter(lambda r: r[10] != "-1" or r[11] != "", rows)

    return out


def process_text(text):
    # Replaces "O" by "0" if they are the beginning, middle or end of digits
    text = re.sub(r"(?<=\d)O(?=\d)|(?<=\d)O|O(?=\d)", "0", text)

    # Removes single or double whitespaces between numbers "1 000" becomes "1000"
    text = re.sub("(?<=\d) {1,2}(?=\d)", "", text)

    return text
