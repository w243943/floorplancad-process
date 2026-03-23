import os
import glob
from xml.etree import ElementTree as ET
from PIL import Image
import tempfile
from utils_dataset import svg2png, svg_reader, svg_writer
from functools import partial
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm  # pip install tqdm
import time
import shutil

SVG_CATEGORIES = [
    # 1-6 doors
    {"color": [224, 62, 155], "isthing": 1, "id": 1, "name": "single door"},
    {"color": [157, 34, 101], "isthing": 1, "id": 2, "name": "double door"},
    {"color": [232, 116, 91], "isthing": 1, "id": 3, "name": "sliding door"},
    {"color": [101, 54, 72], "isthing": 1, "id": 4, "name": "folding door"},
    {"color": [172, 107, 133], "isthing": 1, "id": 5, "name": "revolving door"},
    {"color": [142, 76, 101], "isthing": 1, "id": 6, "name": "rolling door"},
    # 7-10 window
    {"color": [96, 78, 245], "isthing": 1, "id": 7, "name": "window"},
    {"color": [26, 2, 219], "isthing": 1, "id": 8, "name": "bay window"},
    {"color": [63, 140, 221], "isthing": 1, "id": 9, "name": "blind window"},
    {"color": [233, 59, 217], "isthing": 1, "id": 10, "name": "opening symbol"},
    # 11-27: furniture
    {"color": [122, 181, 145], "isthing": 1, "id": 11, "name": "sofa"},
    {"color": [94, 150, 113], "isthing": 1, "id": 12, "name": "bed"},
    {"color": [66, 107, 81], "isthing": 1, "id": 13, "name": "chair"},
    {"color": [123, 181, 114], "isthing": 1, "id": 14, "name": "table"},
    {"color": [94, 150, 83], "isthing": 1, "id": 15, "name": "TV cabinet"},
    {"color": [66, 107, 59], "isthing": 1, "id": 16, "name": "Wardrobe"},
    {"color": [145, 182, 112], "isthing": 1, "id": 17, "name": "cabinet"},
    {"color": [152, 147, 200], "isthing": 1, "id": 18, "name": "gas stove"},
    {"color": [113, 151, 82], "isthing": 1, "id": 19, "name": "sink"},
    {"color": [112, 103, 178], "isthing": 1, "id": 20, "name": "refrigerator"},
    {"color": [81, 107, 58], "isthing": 1, "id": 21, "name": "airconditioner"},
    {"color": [172, 183, 113], "isthing": 1, "id": 22, "name": "bath"},
    {"color": [141, 152, 83], "isthing": 1, "id": 23, "name": "bath tub"},
    {"color": [80, 72, 147], "isthing": 1, "id": 24, "name": "washing machine"},
    {"color": [100, 108, 59], "isthing": 1, "id": 25, "name": "squat toilet"},
    {"color": [182, 170, 112], "isthing": 1, "id": 26, "name": "urinal"},
    {"color": [238, 124, 162], "isthing": 1, "id": 27, "name": "toilet"},
    # 28:stairs
    {"color": [247, 206, 75], "isthing": 1, "id": 28, "name": "stairs"},
    # 29-30: equipment
    {"color": [237, 112, 45], "isthing": 1, "id": 29, "name": "elevator"},
    {"color": [233, 59, 46], "isthing": 1, "id": 30, "name": "escalator"},
    # 31-35: uncountable
    {"color": [172, 107, 151], "isthing": 0, "id": 31, "name": "row chairs"},
    {"color": [102, 67, 62], "isthing": 0, "id": 32, "name": "parking spot"},
    {"color": [167, 92, 32], "isthing": 0, "id": 33, "name": "wall"},
    {"color": [121, 104, 178], "isthing": 0, "id": 34, "name": "curtain wall"},
    {"color": [64, 52, 105], "isthing": 0, "id": 35, "name": "railing"},
    {"color": [0, 0, 0], "isthing": 0, "id": 0, "name": "bg"},
]


def process_svg(svg_data):
    parsing_list = svg_reader(svg_data)
    instance_dict = {}
    semantic_to_isthing = {cat["id"]: cat["isthing"] for cat in SVG_CATEGORIES}
    for elem in parsing_list:
        instance_id = elem.get('instance-id')
        semantic_id = elem.get('semantic-id')
        if instance_id != "-1" and instance_id is not None:
            if semantic_id is not None:
                try:
                    semantic_id_int = int(semantic_id)
                    if semantic_to_isthing.get(semantic_id_int, 1) == 0:
                        continue
                except ValueError:
                    continue
            if instance_id not in instance_dict:
                instance_dict[instance_id] = []
            instance_dict[instance_id].append(elem)
    return instance_dict


def create_instance_svg(svg_path, instance_elems, out_svg_path):
    parsing_list = svg_reader(svg_path)
    new_list = []
    for line in parsing_list:
        tag = line["tag"].split("svg}")[-1]
        if tag in ["svg", "g"]:
            new_list.append(line)
            continue
        if line in instance_elems:
            if "stroke" in line:
                line["stroke"] = "rgb(255,255,255)"
            new_list.append(line)
    svg_writer(new_list, out_svg_path)


def generate_instance_png(svg_path, instance_dict, png_dir,  output_width, output_height):
    # 创建 png 和 txt 子目录
    png_out_dir = os.path.join(png_dir, "png")
    txt_out_dir = os.path.join(png_dir, "txt")
    os.makedirs(png_out_dir, exist_ok=True)
    os.makedirs(txt_out_dir, exist_ok=True)

    tmp_dir = tempfile.mkdtemp(prefix="instance_svg_", dir=png_dir)
    try:
        for instance_id, elems in instance_dict.items():
            if len(elems) <= 1:
                continue
            tmp_svg = os.path.join(tmp_dir, f"instance_{instance_id}.svg")
            out_png = os.path.join(png_out_dir, f"instance_{instance_id}_mask.png")
            create_instance_svg(svg_path, elems, tmp_svg)
            # svg2png(tmp_svg, out_png, output_width = output_width, output_height = output_height)
            command = "cairosvg {} -o {}  --output-width {}  --output-height {}".format(tmp_svg, out_png,  output_width, output_height)
            os.system(command)
            time.sleep(0.01)
            img = Image.open(out_png).convert('L')
            threshold = 128
            img = img.point(lambda p: p > threshold and 255)
            img.save(out_png)
            semantic_id = elems[0].get('semantic-id')
            if semantic_id:
                txt_path = os.path.join(txt_out_dir, f"instance_{instance_id}_mask.txt")
                with open(txt_path, 'w') as f:
                    f.write(f'Semantic ID: {semantic_id}\n')
    finally:
        shutil.rmtree(tmp_dir)
    print(f"Finished processing {os.path.basename(svg_path)}")


def process_single_svg(svg_file, output_root,  output_width, output_height):
    base_name = os.path.splitext(os.path.basename(svg_file))[0]
    single_output_dir = os.path.join(output_root, f"{base_name}")
    instance_dict = process_svg(svg_file)
    generate_instance_png(svg_file, instance_dict, single_output_dir,  output_width, output_height)
    return single_output_dir


def batch_process_svgs(input_dir, output_root,  output_width, output_height, num_threads=4):
    svg_files = glob.glob(os.path.join(input_dir, "*.svg"))
    results = []
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = {
            executor.submit(process_single_svg, svg, output_root,  output_width, output_height): svg
            for svg in svg_files
        }
        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing SVGs"):
            try:
                res = future.result()
                results.append(res)
            except Exception as e:
                print(f"Error processing {futures[future]}: {e}")
    return results


if __name__ == "__main__":
    input_svg_dir = "/mnt/sda2/wymwork/shiyan_dataset/test_svg"
    output_root = "/mnt/sda2/wymwork/shiyan_dataset/test_box"
    scale = 10.24
    num_threads = 4

    batch_process_svgs(input_svg_dir, output_root, scale, num_threads)