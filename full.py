import os
from box import batch_process_svgs  # SVG -> PNG/TXT
from vis_box import process_all_images  # PNG -> CSV
from box2coco import csv_to_coco  # CSV+PNG -> COCO

def full_pipeline(svg_dir, output_root, output_width, output_height, coco_json_path, num_threads=4):
    """
    一步完成SVG->PNG/TXT->CSV->COCO
    """
    print("\n=== Step 1: SVG -> PNG/TXT ===")
    batch_process_svgs(svg_dir, output_root, output_width, output_height, num_threads=num_threads)

    print("\n=== Step 2: PNG -> CSV ===")
    process_all_images(output_root)

    print("\n=== Step 3: CSV + PNG -> COCO ===")
    csv_to_coco(output_root, coco_json_path)

    print("\n=== All steps completed! ===")


svg_dir = "/mnt/sda2/wymwork/shiyan_dataset/test_svg"
output_root = "/mnt/sda2/wymwork/shiyan_dataset/test_box3"

output_width = 1024
output_height = 1024
coco_json_path = os.path.join(output_root, "coco_test.json")
full_pipeline(svg_dir, output_root, output_width, output_height, coco_json_path)

