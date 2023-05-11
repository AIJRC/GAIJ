import PIL
import tesserocr

import pandas as pd
from io import StringIO

import os
import logging
import queue
import concurrent.futures


def ocr_image(image_path, queue, preprocess=True):
    api = None
    try:
        api = queue.get(block=True, timeout=600)

        tsv = "level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext\n"
        with PIL.Image.open(image_path) as image:
            for page in PIL.ImageSequence.Iterator(image):
                api.SetImage(page)
                data = api.GetTSVText(0)
                tsv += data
        return tsv
    except queue.Empty:
        return None
    finally:
        if api is not None:
            queue.put(api)


if __name__ == "__main__":
    NUM_THREADS = 8
    os.environ['OMP_THREAD_LIMIT'] = '1'

    tesserocr_queue = queue.Queue(maxsize=NUM_THREADS)
    for _ in range(NUM_THREADS):
        api = tesserocr.PyTessBaseAPI(
            lang="nor+eng", psm=6
        )  # appears to be better at digit recognition than just 'nor'
        api.SetVariable(
            "preserve_interword_spaces", "1"
        )  # optimal for extracting table-like data
        tesserocr_queue.put(api)

    tifs_dir = "./tifs/"
    csvs_dir = "./csvs/"

    # Find all files to be OCR'ed
    images = list(filter(lambda x: x.endswith(".tif"), os.listdir(tifs_dir)))
    ocred = list(filter(lambda x: x.endswith(".csv"), os.listdir(csvs_dir)))
    missing_images = set(images).difference(set(map(lambda x: os.path.splitext(x)[0] + ".tif", ocred)))

    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        def procedure(image_name):
            tsv = ocr_image(tifs_dir + image_name, tesserocr_queue)
            try:
                df = pd.read_table(StringIO(tsv), sep="\t", quoting=3)
                df.to_csv(csvs_dir + os.path.splitext(image_name)[0] + ".csv", index=False)
            except Exception as e:
                logging.warning("Failed writting {}".format(image_name), e)

        executor.map(procedure, missing_images)
