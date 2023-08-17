import cv2
import numpy as np


def get_FundamentalMat(img1, img2):
    # 创建SIFT检测器
    sift = cv2.SIFT_create()

    # 在两张图片中检测关键点并计算描述符
    keypoints1, descriptors1 = sift.detectAndCompute(img1, None)
    keypoints2, descriptors2 = sift.detectAndCompute(img2, None)

    # 进行特征点匹配
    matcher = cv2.BFMatcher()
    matches = matcher.knnMatch(descriptors1, descriptors2, k=2)

    good_matches = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good_matches.append(m)

    # 获取匹配的特征点对的坐标
    src_pts = np.array([keypoints1[m.queryIdx].pt for m in good_matches])
    dst_pts = np.array([keypoints2[m.trainIdx].pt for m in good_matches])

    # 计算基础矩阵
    F, mask = cv2.findFundamentalMat(src_pts, dst_pts, cv2.FM_RANSAC)
    return F


# 坐标变换，传入两张图片中的坐标和基础矩阵，返回第二张图片中的坐标
def transform_point(x1, y1, F, img2):
    # 将第一张图片中的点转换为齐次坐标
    pt1 = np.array([x1, y1, 1])

    # 计算极线
    epiline = F @ pt1

    # 在第二张图片上搜索匹配点
    line_coefficients = np.squeeze(epiline)
    y_range = range(img2.shape[0])
    x_range = [int((-line_coefficients[1] * y - line_coefficients[2]) / line_coefficients[0]) for y in y_range]

    # 选择与第一张图片中的特征点最接近的点
    min_distance = float('inf')
    best_match = (0, 0)
    for y, x in zip(y_range, x_range):
        if 0 <= x < img2.shape[1]:
            distance = np.linalg.norm(np.array([y, x]) - np.array([y1, x1]))
            if distance < min_distance:
                min_distance = distance
                best_match = (y, x)

    # 获取第二张图片中的像素坐标
    return best_match[1], best_match[0]


# 坐标变换，传入第一张图中的坐标，返回第二张图片中的坐标
def transform_line(pre_img, img, ps):
    # 计算基础矩阵
    F = get_FundamentalMat(pre_img, img)
    # 计算第二帧中斑马线的坐标
    ps_ = []
    for x, y in ps:
        # 坐标转换
        ps_.append(transform_point(x, y, F, img))
    return ps_
