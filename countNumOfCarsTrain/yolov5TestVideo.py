# -*- coding: utf-8 -*-
# @Time : 2023/3/15 15:23

import cv2
import torch
import numpy as np
import math


# 将 x y w h angle 转换为四条线段坐标
def get_rotated_rect_lines(center_x, center_y, w, h, angle):
    # 计算矩形的四个顶点坐标
    theta = math.radians(angle)
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)

    w_half = w / 2
    h_half = h / 2

    x1 = int(center_x + cos_t * (-w_half) + sin_t * (-h_half))
    y1 = int(center_y - sin_t * (-w_half) + cos_t * (-h_half))
    x2 = int(center_x + cos_t * (w_half) + sin_t * (-h_half))
    y2 = int(center_y - sin_t * (w_half) + cos_t * (-h_half))
    x3 = int(center_x + cos_t * (w_half) + sin_t * (h_half))
    y3 = int(center_y - sin_t * (w_half) + cos_t * (h_half))
    x4 = int(center_x + cos_t * (-w_half) + sin_t * (h_half))
    y4 = int(center_y - sin_t * (-w_half) + cos_t * (h_half))

    # 构建四条线段的坐标数组
    return np.array([[x1, y1], [x2, y2], [x3, y3], [x4, y4]])


# 加载YOLOv5模型
path = r"F:\zhangBo\oneDrive\code\python\countNumOfCars\yolov5-master"
model = torch.hub.load(source='local', path=path + r"\best.pt", repo_or_dir=path,
                       model="custom", force_reload=True)

# 指定输入视频文件
video_path = r'../../video/test.mp4'

# 打开视频文件
cap = cv2.VideoCapture(video_path)



# 指定输出视频文件
output_path = r'../../video/output/output.avi'

# 定义输出视频编解码器
fourcc = cv2.VideoWriter_fourcc(*'MJPG')

# 创建输出视频对象
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

# 循环读取视频帧并进行车辆检测
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # 将帧转换为RGB颜色空间
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 使用YOLOv5进行车辆检测
    results = model(frame)

    # 从结果中提取车辆检测框并绘制到原始帧上
    for x1, y1, x2, y2, conf, cls in results.xyxy[0].cpu().numpy():
        if int(cls) == 0:  # 检测是否为汽车（class ID为0）
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
            print(x1, x2, y1, y2)

    # 将帧转换回BGR颜色空间并写入输出视频
    out.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

# 释放资源
cap.release()
out.release()
cv2.destroyAllWindows()
