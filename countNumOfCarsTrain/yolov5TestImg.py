# -*- coding: utf-8 -*-
# @Time : 2023/3/23 9:09

import torch
import cv2

# 加载YOLOv5模型
path = r"F:\zhangBo\oneDrive\code\python\countNumOfCars\yolov5-master"
model = torch.hub.load(source='local', path=path + r"weights\best-DETRAC-5000.pt", repo_or_dir=path,
                       model="custom", force_reload=True)

# 读入图片
# img_path = r"F:\zhangBo\oneDrive\code\python\countNumOfCars\video\1.png"
# img_path = r"F:\zhangBo\oneDrive\code\python\countNumOfCars\video\small.png"
img_path = r"F:\下载\111.png"
img = cv2.imread(img_path)

results = model(img)
# 从结果中提取车辆检测框并绘制到原始帧上
for x1, y1, x2, y2, conf, cls in results.xyxy[0].cpu().numpy():
    if True:  # 检测是否为汽车（class ID为0）
        cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)

cv2.imshow("img", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
