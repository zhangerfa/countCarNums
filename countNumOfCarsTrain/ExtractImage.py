# -*- coding: utf-8 -*-
# @Time : 2023/4/10 8:49

# ------------------ 从视频中提取图片
import cv2
import os


# 截取视频中帧保存到本地
# path: 视频路径
# gap: 截取帧间隔
# save_path: 保存路径
# prefix: 保存文件名的前缀
# 最终文件保存为：{save_path}\{prefix}_{count}.jpg
def get_images(path, gap, save_path, prefix):
    # 创建VideoCapture对象读取视频
    cap = cv2.VideoCapture(path)

    # 保存路径创建
    if not os.path.exists(save_path):
        # 如果文件路径不存在，则创建该路径
        os.makedirs(save_path)

    # 定义帧数计数器
    imgCount = 0
    count = 0

    while cap.isOpened():
        # 读取视频帧
        ret, frame = cap.read()

        if ret:
            # 如果读取成功，则将计数器加1
            count += 1
            if count % gap == 0:
                imgCount += 1
                # 每5帧提取一张图片并保存到本地
                cv2.imwrite(fr'{save_path}\{prefix}_{imgCount}.jpg', frame)
                count = 0
        else:
            break

    # 释放资源
    cap.release()


# 设置读取视频的路径
video_path = r'F:\zhangBo\video'
for videoName in ['MoLiGongGuan', 'JinXinGuoJi']:
    get_images(video_path + rf"\{videoName}.mp4", 5, rf'F:\zhangBo\train\JianKong\{videoName}', videoName)
    print(f"{videoName}.mp4执行完毕")
