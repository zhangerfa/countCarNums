# -*- coding: utf-8 -*-

import os
import xml.etree.ElementTree as ET

# DETRAC-Train-Annotations-XML---内涵xml文件
xmlDir=r"F:\zhangBo\train\DETRAC\DETRAC-Train-Annotations-XML"
# 转换的xml文件保存位置
new_dir=r"F:\zhangBo\train\DETRAC\Annotations"

# 转换xml文件
def bboxes2xml(folder, img_name, width, height, gts, xml_save_to):
    xml_file = open((xml_save_to + '\\' + img_name + '.xml'), 'w')
    xml_file.write('<annotation>\n')
    xml_file.write('    <folder>' + folder + '</folder>\n')
    xml_file.write('    <filename>' + str(img_name) + '.jpg' + '</filename>\n')
    xml_file.write('    <size>\n')
    xml_file.write('        <width>' + str(width) + '</width>\n')
    xml_file.write('        <height>' + str(height) + '</height>\n')
    xml_file.write('        <depth>3</depth>\n')
    xml_file.write('    </size>\n')

    for gt in gts:
        xml_file.write('    <object>\n')
        xml_file.write('        <name>' + str(gt[0]) + '</name>\n')
        xml_file.write('        <pose>Unspecified</pose>\n')
        xml_file.write('        <truncated>0</truncated>\n')
        xml_file.write('        <difficult>0</difficult>\n')
        xml_file.write('        <bndbox>\n')
        xml_file.write('            <xmin>' + str(gt[1]) + '</xmin>\n')
        xml_file.write('            <ymin>' + str(gt[2]) + '</ymin>\n')
        xml_file.write('            <xmax>' + str(gt[3]) + '</xmax>\n')
        xml_file.write('            <ymax>' + str(gt[4]) + '</ymax>\n')
        xml_file.write('        </bndbox>\n')
        xml_file.write('    </object>\n')

    xml_file.write('</annotation>')
    xml_file.close()

for xmlNames in os.listdir(xmlDir):
    xmlPath=os.path.join(xmlDir,xmlNames)   # xml文件路径
    # print(xmlPath)
    tree = ET.parse(xmlPath)
    root = tree.getroot()
    findall_frames = root.findall("frame")            # frame标签列表
    fileName=root.attrib["name"]
    # print(fileName)


    for findall_frame in findall_frames:
        attrib = findall_frame.attrib["num"]
        zfill = attrib.zfill(5)
        imageName="img"+zfill        # 图像的名称
        print("--------------------------{}".format(imageName))
        gts = []
        target_list = findall_frame.findall("target_list")[0]

        findall_targets = target_list.findall("target")      # target对应的标签
        for findall_target in findall_targets:
            gt_temp = []
            LabelName = findall_target.findall("attribute")[0].attrib["vehicle_type"]       # 获取标签类别
            gt_temp.append(LabelName)
            box_Dict = findall_target.findall("box")[0].attrib   # 标注物体坐标
            xmin = float(box_Dict["left"])
            ymin = float(box_Dict["top"])
            width = float(box_Dict["width"])
            height = float(box_Dict["height"])
            xmax=xmin+width
            ymax=ymin+height
            gt_temp.append(int(xmin))
            gt_temp.append(int(ymin))
            gt_temp.append(int(xmax))
            gt_temp.append(int(ymax))
            gts.append(gt_temp)

        print(gts)
        folder = "images"
        img_name = fileName + "__" + imageName
        width = 960                         # 图像的像素
        height = 540                        # 图像像素
        xml_save_to = new_dir               # 生成的xml保存位置

        # 生成xml文件
        bboxes2xml(folder, img_name, width, height, gts, xml_save_to)
        print("done")

        print("----------------------------------------")
