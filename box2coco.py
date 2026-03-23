import os
import cv2
import json
import pandas as pd

# 类别名称列表（根据你的实际情况修改）
wordname_16 = [
    "bg",
    "wall",                 
    "railing",              
    "single_door",          
    "double_door",         
    "sliding_door",        
    "folding_door",        
    "revolving_door",      
    "rolling_door",        
    "window",              
    "bay_window",          
    "blind_window",        
    "opening_symbol",      
    "sofa",                
    "bed",                 
    "chair",               
    "table",               
    "tv_cabinet",          
    "wardrobe",            
    "cabinet",             
    "refrigerator",        
    "aircondition",       
    "gas_stove",           
    "sink",                
    "bath",                
    "bath_tub",            
    "washing_machine",     
    "squat_toilet",        
    "urinal",              
    "toilet",              
    "stairs",              
    "elevator",            
    "escalator",           
    "curtain_wall",        
    "row_chairs",          
    "parking_spot",        
]



def csv_to_coco(src_root, dest_file):
    """
    src_root: 数据根目录，包含多个子文件夹（如0000-0016, 0777-0168等）
    dest_file: 输出的COCO格式json文件路径
    """
    data_dict = {
        'info': {
            'contributor': 'captain group',
            'data_created': '2026',
            'description': 'Converted from CSV format to COCO format.',
            'version': '1.0',
            'year': 2026
        },
        'images': [],
        'categories': [],
        'annotations': []
    }
    
    # 添加类别
    for idx, name in enumerate(wordname_16):
        single_cat = {'id': idx + 1, 'name': name}
        data_dict['categories'].append(single_cat)
    
    inst_count = 1
    image_id = 1
    
    # 遍历所有子文件夹
    for subdir in sorted(os.listdir(src_root)):
        subdir_path = os.path.join(src_root, subdir)
        
        if not os.path.isdir(subdir_path):
            continue
        
        print(f"Processing {subdir}...")
        
        # 查找png文件夹中的图片
        png_folder = os.path.join(subdir_path, 'png')
        txt_folder = os.path.join(subdir_path, 'txt')
        
        if not os.path.exists(png_folder):
            continue
        
        # 获取所有png图片
        png_files = [f for f in os.listdir(png_folder) if f.endswith('.png')]
        
        for png_file in png_files:
            basename = os.path.splitext(png_file)[0]
            
            # 读取图片获取尺寸
            image_path = os.path.join(png_folder, png_file)
            img = cv2.imread(image_path)
            
            if img is None:
                print(f"Warning: Cannot read image {image_path}")
                continue
            
            height, width, c = img.shape
            
            # 添加image信息
            single_image = {
                'file_name': os.path.join(subdir, 'png', png_file),
                'id': image_id,
                'width': width,
                'height': height
            }
            data_dict['images'].append(single_image)
            
            # 读取对应的txt文件获取类别
            txt_file = os.path.join(txt_folder, basename + '.txt')
            category_id = 1  # 默认bg
            instance_number = basename.split('_mask')[0]
            
            if os.path.exists(txt_file):
                try:
                    with open(txt_file, 'r') as f:
                        content = f.read().strip()
                        category_id = content.split(':')[1].strip()
                        # if content in wordname_16:
                        #     category_id = wordname_16.index(content) + 1
                except Exception as e:
                    print(f"Warning: Cannot read txt file {txt_file}: {e}")
            
            # 读取对应的csv文件获取标注
            csv_file = os.path.join(subdir_path, 'box', basename + '_box.csv')
            
            if os.path.exists(csv_file):
                try:
                    df = pd.read_csv(csv_file)
                    
                    for _, row in df.iterrows():
                        center_x = float(row['center_x'])
                        center_y = float(row['center_y'])
                        w = float(row['width'])
                        h = float(row['height'])
                        angle = float(row['angle'])

                        x1 = float(row['corner_1_x'])
                        y1 = float(row['corner_1_y'])

                        x2 = float(row['corner_2_x'])
                        y2 = float(row['corner_2_y'])

                        x3 = float(row['corner_3_x'])
                        y3 = float(row['corner_3_y'])

                        x4 = float(row['corner_4_x'])
                        y4 = float(row['corner_4_y'])

                        poly = [x1, y1, x2, y2, x3, y3, x4, y4]
                        # poly = TuplePoly2Poly(poly)
                        poly = list(map(int, poly))
                        
        
                                   
                        # 计算面积
                        area = w * h
                        
                        single_obj = {
                            'id': inst_count,
                            'image_id': image_id,
                            'category_id': category_id,
                            'segmentation': [poly],
                            'rotate_caption':[center_x, center_y, w, h, angle],
                            'instance_number':instance_number,
                            'area': area,
                            'bbox': [poly],
                            'iscrowd': 0
                        }
                        data_dict['annotations'].append(single_obj)
                        inst_count += 1
                        
                except Exception as e:
                    print(f"Warning: Cannot process csv file {csv_file}: {e}")
            
        image_id += 1
    
    # 保存为json
    with open(dest_file, 'w', encoding='utf-8') as f_out:
        json.dump(data_dict, f_out, ensure_ascii=False, indent=2)
    
    print(f"\nConversion completed!")
    print(f"Total images: {len(data_dict['images'])}")
    print(f"Total annotations: {len(data_dict['annotations'])}")
    print(f"Output saved to: {dest_file}")

if __name__ == '__main__':
    src_root = "/mnt/sda2/wymwork/shiyan_dataset/test_box"  # 修改为你的数据根目录
    dest_file = "/mnt/sda2/wymwork/shiyan_dataset/test_box/coco_test.json"
    csv_to_coco(src_root, dest_file)