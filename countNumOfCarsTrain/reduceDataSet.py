# -*- coding: utf-8 -*-
# @Time : 2023/4/6 19:39

import os

base_path = r'F:\zhangBo\train\DETRAC-small'  # 指定文件夹路径

for p in [r'\images\test', r'\images\train', r'\Annotations\train', r'\Annotations\test']:
    path = base_path + p
    files = os.listdir(path)  # 获取该路径下所有文件和文件夹
    for i in range(len(files)):
        if i % 2 != 0:
            os.remove(os.path.join(path, files[i]))
    print(path + "执行完毕")
