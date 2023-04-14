# -*- coding: utf-8 -*-
# @Time : 2023/4/6 19:39

import os


# 将文件移至目标路径
import shutil


def moveFiles(path, save_path):
    files = os.listdir(path)  # 获取该路径下所有文件和文件夹
    for i in range(len(files)):
        if 1200 < int(files[i].split('_')[1].split('.')[0]) <= 1600:
            shutil.copy(path+ '\\' + files[i], save_path + '\\' + files[i])
    print(path + "执行完毕")


def removeFiles(path):
    files = os.listdir(path)  # 获取该路径下所有文件和文件夹
    for i in range(len(files)):
        if i < 400:
            os.remove(os.path.join(path, files[i]))
    print(path + "执行完毕")

# base_path = r'F:\zhangBo\train\DETRAC-small'  # 指定文件夹路径
# for p in [r'\images\test', r'\images\train', r'\Annotations\train', r'\Annotations\test']:
#     path = base_path + p
#     removeFiles(path)

path = r'F:\zhangBo\train\JianKong\JinXinGuoJi'
save_path = r'F:\zhangBo\train\JianKong\JinXinGuoJi-small\周园理'
moveFiles(path, save_path)