# -*- coding: utf-8 -*-
# @Time : 2023/3/16 11:08

from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction
import cv2
import time

start_time = time.time()

# 建立检测对象
detection_model = AutoDetectionModel.from_pretrained(
    model_type='yolov5',
    model_path=r"pt/yolov5x.pt",
    config_path=r"pt/yolov5x.yaml",
    confidence_threshold=0.4,
    device="cuda:0"
)

# 打开原视频
path = r"../video/test.mp4"
video = cv2.VideoCapture(path)

# 读取视频的帧速率和尺寸
fps = int(video.get(cv2.CAP_PROP_FPS))
width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 创建输出视频的写入器
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter("../video/output/output.mp4", fourcc, fps, (width, height))

# 遍历视频的每一帧
c = 0 # 记录当前为第几帧
second_count = 0 # 已处理完的视频时长
time1 = time.time()
while True:
    # 读取一帧
    ret, frame = video.read()

    # 如果读取失败，则跳出循环
    if not ret:
        break

    # 处理当前帧
    result = get_sliced_prediction(
        frame,
        detection_model,
        slice_height=256,
        slice_width=256,
        overlap_height_ratio=0.2,
        overlap_width_ratio=0.2
    )

    '''
    object_prediction_list:{
        bbox: BoundingBox: <(160.22396087646484, 347.084924697876, 183.03107833862305, 358.92453384399414), w: 22.807117462158203, h: 11.839609146118164>,
         mask: None,
         score: PredictionScore: <value: 0.4676949679851532>,
         category: Category: <id: 67, name: car>>,
         }
    '''

    # 从结果中提取车辆检测框并绘制到原始帧上
    for pre_ls in result.object_prediction_list:
        # 检测框坐标
        xyxy = pre_ls.bbox.to_xyxy()
        x1 = xyxy[0]
        y1 = xyxy[1]
        x2 = xyxy[2]
        y2 = xyxy[3]
        # 置信度
        conf = pre_ls.score.value
        # 类别{id, train}
        cls = pre_ls.category

        if cls.id == 67:
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)

    # 将处理后的帧写入输出视频
    out.write(frame)
    c = c + 1
    time2 = time.time()
    if (c % fps == 0):
        second_count = second_count + 1
        print("已处理完视频时长为：",second_count, "s", "上一秒视频处理花费:", time2 - time1, "s")
        time1 = time2

# 释放资源
video.release()
out.release()
cv2.destroyAllWindows()

end_time = time.time()

print("视频处理完毕，共花费", end_time - start_time, "s")


