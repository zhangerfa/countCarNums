# -*- coding: utf-8 -*-
# @Time : 2023/4/6 18:21
import os
import xml.etree.ElementTree as ET

folder_path = r'F:\zhangBo\train\DETRAC\Annotations\train'  # 更改为您的文件夹路径

res = {}
for filename in os.listdir(folder_path):
    if not filename.endswith('.xml'):  # 如果不是xml文件，请跳过
        continue
    filepath = os.path.join(folder_path, filename)
    tree = ET.parse(filepath)
    root = tree.getroot()
    for elem in root.findall('.//*'):
        for obj in root.iter('object'):
            cls = obj.find('name').text
            if cls not in ['car', 'bus']:
                print(cls)
                obj.find('name').text = 'car'
    tree.write(filepath)