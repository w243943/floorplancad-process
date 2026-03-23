import os
import cv2
import numpy as np
import pandas as pd

# 根目录
root_dir = "/mnt/sda2/wymwork/shiyan_dataset/test_box"

def process_single_image(image_path, box_output_dir):
    """处理单张二值图，计算所有黑色线条的整体最小旋转包围框"""
    
    # 1. 读取图像（灰度模式）
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"❌ 无法读取图像: {image_path}")
        return None
    
    # 2. 反转图像：白底黑线 → 黑底白线
    # img_inv = cv2.bitwise_not(img)
    
    # 3. 二值化
    _, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    
    # 4. 查找所有轮廓
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        print(f"⚠️ 未找到轮廓: {image_path}")
        return None
    
    # 5. 合并所有轮廓为一个整体轮廓
    all_points = np.vstack([cnt for cnt in contours])
    overall_contour = cv2.convexHull(all_points)
    
    # 6. 计算最小旋转包围框
    min_rect = cv2.minAreaRect(overall_contour)
    box_points = cv2.boxPoints(min_rect)
    box_points = np.int32(box_points)
    
    # 7. 可视化：在原图上绘制最小旋转包围框
    img_color = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(img_color, [box_points], 0, (0, 255, 0), 2)
    
    # 8. 保存可视化后的图像到box目录
    img_name = os.path.splitext(os.path.basename(image_path))[0]
    vis_path = os.path.join(box_output_dir, f"{img_name}_boxed.png")
    cv2.imwrite(vis_path, img_color)
    # print(f"✅ 已保存可视化图像: {vis_path}")
    
    # 9. 保存box信息到CSV文件
    box_info = {
        'center_x': round(min_rect[0][0], 2),
        'center_y': round(min_rect[0][1], 2),
        'width': round(min_rect[1][0], 2),
        'height': round(min_rect[1][1], 2),
        'angle': round(min_rect[2], 2),
        'corner_1_x': int(box_points[0][0]),
        'corner_1_y': int(box_points[0][1]),
        'corner_2_x': int(box_points[1][0]),
        'corner_2_y': int(box_points[1][1]),
        'corner_3_x': int(box_points[2][0]),
        'corner_3_y': int(box_points[2][1]),
        'corner_4_x': int(box_points[3][0]),
        'corner_4_y': int(box_points[3][1])
    }
    
    csv_path = os.path.join(box_output_dir, f"{img_name}_box.csv")
    df = pd.DataFrame([box_info])
    df.to_csv(csv_path, index=False)
    # print(f"✅ 已保存box信息: {csv_path}")
    
    return box_info

def process_all_images(root_dir):
    """遍历所有子目录，处理每个png图像"""
    
    for sub_dir in os.listdir(root_dir):
        sub_path = os.path.join(root_dir, sub_dir)
        
        if not os.path.isdir(sub_path):
            continue
        
        png_dir = os.path.join(sub_path, 'png')
        box_dir = os.path.join(sub_path, 'box')
        
        if not os.path.exists(png_dir):
            continue
        
        # 创建box目录
        os.makedirs(box_dir, exist_ok=True)
        
        print(f"\n📁 处理目录: {sub_dir}")
        print("-" * 40)
        
        # 处理所有PNG图像
        for file_name in os.listdir(png_dir):
            if file_name.lower().endswith('.png'):
                image_path = os.path.join(png_dir, file_name)
                print(f"\n🔄 处理: {file_name}")
                process_single_image(image_path, box_dir)
    
    print("\n" + "=" * 60)
    print("✅ 全部处理完成!")

if __name__ == "__main__":
    process_all_images(root_dir)