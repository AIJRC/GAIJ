import PIL
import tesserocr
import os
from tqdm import tqdm
import queue
import concurrent.futures
import argparse



def ocr_image(image_path, queue, output_folder):
    api = None
    try:
        api = queue.get(block=True, timeout=600)

        markdown_text = ""
        with PIL.Image.open(image_path) as image:
            for page_num, page in enumerate(PIL.ImageSequence.Iterator(image), 1):
                api.SetImage(page)
                text = api.GetUTF8Text()
                markdown_text += f"# Page {page_num}\n\n{text}\n\n"

        output_filename = os.path.splitext(os.path.basename(image_path))[0] + ".md"
        output_path = os.path.join(output_folder, output_filename)
        os.makedirs(output_folder, exist_ok=True)
        with open(output_path, 'w+', encoding='utf-8') as f:
            f.write(markdown_text)

        return output_path
    except queue.empty:
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
            lang="nor+eng", psm=11, oem=3
        )

        tesserocr_queue.put(api)

    parser = argparse.ArgumentParser(description='OCR image processing')
    parser.add_argument('--tifs_dir', required=True, help='Directory containing TIFF files')
    parser.add_argument('--md_dir', required=True, help='Output directory for Markdown files')
    args = parser.parse_args()

    tifs_dir = args.tifs_dir
    md_dir = args.md_dir

    # Find all files to be OCR'ed
    images = list(filter(lambda x: x.endswith(".tif"), os.listdir(tifs_dir)))
    ocred = list(filter(lambda x: x.endswith(".md"), os.listdir(md_dir)))
    missing_images = set(images).difference(set(map(lambda x: os.path.splitext(x)[0] + ".tif", ocred)))

    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        def procedure(image_name):
            ocr_image(os.path.join(tifs_dir, image_name), tesserocr_queue, md_dir)
        list(tqdm(executor.map(procedure, missing_images), total=len(missing_images), desc="Processing images"))
