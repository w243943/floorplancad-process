# floorplancad-process
## 项目简介
本项目旨在处理并修正 FloorPlanCAD 数据集中的标注错误，并将该数据集中的实例（instance）信息转换为 COCO 数据格式，以便于在目标检测、实例分割等计算机视觉任务中直接使用。

## 主要功能
- **数据修正**：修复了原始 FloorPlanCAD 数据集中存在的标签与真实数据不匹配的错误。
- **格式转换**：将修正后的数据集标注信息转换为标准的 COCO JSON 格式。

## 数据修正说明
在对原始数据集进行检查和可视化时，发现部分类别的标注存在错误。例如，原`single_door` 类别的部分标注实例实际应为 `wall`。

针对此问题，我们全面检查了所有类别，并确定了以下修正后的类别列表，共计 37 个类别（包含背景类 `bg`）：

```python
class = [
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
```
## 使用说明
运行根目录下的 full.py脚本即可完成全流程处理。该脚本整合了以下关键步骤，将原始数据最终转换为COCO格式：

1.矢量图转换：将SVG格式的图纸转换为PNG图像。

2.目标信息提取：从PNG图像中提取目标边界框（bbox）并生成CSV中间文件。

3.格式转换：将CSV文件中的标注信息转换为标准的COCO JSON格式。

最终输出文件为 coco_test.json。
## 注意事项
本项目基于原始 FloorPlanCAD 数据集进行处理，使用前请确保您已拥有并理解原始数据集的许可协议。 修正后的类别列表是本次处理的核心变更，在后续模型训练或评估中应以此为准。
