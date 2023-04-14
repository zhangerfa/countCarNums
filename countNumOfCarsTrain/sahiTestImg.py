# -*- coding: utf-8 -*-
# @Time : 2023/3/20 9:20

# ------------------ 处理一张图片

from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction
from sahi.utils.cv import read_image_as_pil

# 建立检测对象
detection_model = AutoDetectionModel.from_pretrained(
    model_type='yolov5',
    model_path=r"../weights/yolov5x.pt",
    config_path=r"../models/yolov5x.yaml",
    confidence_threshold=0.2,
    device="cuda:0"
)

path = r"F:\下载\test.jpg"
image = read_image_as_pil(path)

result = get_sliced_prediction(
    image,
    detection_model,
    slice_height=200,
    slice_width=200,
    overlap_height_ratio=0.2,
    overlap_width_ratio=0.2
)

'''
result:{
    image
    object_prediction_list:{
        bbox: BoundingBox: <(160.22396087646484, 347.084924697876, 183.03107833862305, 358.92453384399414), w: 22.807117462158203, h: 11.839609146118164>,
         mask: None,
         score: PredictionScore: <value: 0.4676949679851532>,
         category: Category: <id: 67, name: car>>,
     }
}
'''

# 检测结果可视化
result.export_visuals(export_dir=r"F:\下载", hide_labels=True)
