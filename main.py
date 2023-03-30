import tracker
from detector import Detector
import cv2

import os

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'


# ----------------------------- 画检测线辅助函数
# 画检测线时的鼠标回调函数
def draw_line(event, x, y, flags, param):
    global start_x, start_y, end_x, end_y
    # 当按下左键时返回起始位置坐标
    if event == cv2.EVENT_LBUTTONDOWN:
        start_x, start_y = x, y
    elif event == cv2.EVENT_LBUTTONUP:
        end_x, end_y = x, y
        cv2.line(img, (start_x, start_y), (end_x, end_y), (0, 0, 255), 5)


# ------------------------------------ 直线与矩形相交判定
# 叉积判定
def cross(p1, p2, p3):
    x1 = p2[0] - p1[0]
    y1 = p2[1] - p1[1]
    x2 = p3[0] - p1[0]
    y2 = p3[1] - p1[1]
    return x1 * y2 - x2 * y1


# 判断两线段是否相交
def segment(p1, p2, p3, p4):
    # 矩形判定，以l1、l2为对角线的矩形必相交，否则两线段不相交
    if (max(p1[0], p2[0]) >= min(p3[0], p4[0])  # 矩形1最右端大于矩形2最左端
            and max(p3[0], p4[0]) >= min(p1[0], p2[0])  # 矩形2最右端大于矩形1最左端
            and max(p1[1], p2[1]) >= min(p3[1], p4[1])  # 矩形1最高端大于矩形2最低端
            and max(p3[1], p4[1]) >= min(p1[1], p2[1])):  # 矩形2最高端大于矩形1最低端
        if (cross(p1, p2, p3) * cross(p1, p2, p4) <= 0
                and cross(p3, p4, p1) * cross(p3, p4, p2) <= 0):
            D = 1
        else:
            D = 0
    else:
        D = 0
    return D


def check_intersect(l1, l2, sq):
    # 检测点是否在矩形内
    if (sq[0] <= l1[0] <= sq[2] and sq[1] <= l1[1] <= sq[3]) or \
            (sq[0] <= l2[0] <= sq[2] and sq[1] <= l2[1] <= sq[3]):
        return 1
    else:
        # 检测矩形边是否与直线相交
        p1 = [sq[0], sq[1]]
        p2 = [sq[2], sq[3]]
        p3 = [sq[2], sq[1]]
        p4 = [sq[0], sq[3]]
        if segment(l1, l2, p1, p2) or segment(l1, l2, p3, p4):
            return 1
        else:
            return 0


# ------------------------------------车辆通过交叉口驶入-驶出点提取的辅助函数
# 获取车辆是否第一次越过检测线及驶入交叉口的入口道（检测线）id，返回值(是否第一次越过检测线, 入口道id)
#   如果车辆越过检测线
#       第一次越过检测线，则此检测线为其驶入交叉口的入口道，返回(True, 入口道id)；
#       非第一次越过检测线，则找到其驶入入口道的检测线id，返回(False, 入口道id)
#   如果未越过检测线返回(False, None)
#
# enter_lane_set: 检测线起讫点坐标（x1 y1 x2 y2）
# car_box: 车辆检测框左上和右下坐标（x1 y1 x2 y2）
def get_enter_lane():
    # 检测当前车辆是否越过检测线
    for line_id, line_pos in enter_lane_set.items():
        lx1, ly1, lx2, ly2 = line_pos
        if check_intersect((lx1, ly1), (lx2, ly2), car_box):
            # 当车辆越过一条检测线时，判断该车辆是否已从某进口道驶入
            for enter_id, enter_set in enter_set_dict.items():
                if str(track_id) in enter_set:
                    return False, None
            return True, line_id
    return False, None


if __name__ == '__main__':
    # -------------------------------------------读入并获取视频信息
    # 打开视频
    video_path = r'..\video\70m.mp4'
    capture = cv2.VideoCapture(video_path)
    # 获取视频FPS和尺寸
    fps = capture.get(cv2.CAP_PROP_FPS)
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # -------------------------------------------画检测线
    # 初始化检测线---> 得到检测线坐标集合 enter_lane_set
    print("开始画检测线")
    print('''鼠标点击检测线起点，拖至检测线重点松开
       画好检测线后，按下e w s n来表示这条检测线是东 西 南 北哪个方向的检测线，小写字母表示入口道，大写字母表示出口道
       当画完所有检测线时按 s 退出''')
    ret, img = capture.read(0)
    ZERO = 1e-9
    start_x, start_y, end_x, end_y = -1, -1, -1, -1
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    # 创建鼠标点击事件：点击和松开时将坐标赋予 start_x, start_y, end_x, end_y
    cv2.setMouseCallback('image', draw_line)
    enter_lane_set = {}  # 入口道检测线坐标集合
    exit_lane_set = {}  # 出口道检测线坐标集合
    while 1:
        cv2.imshow('image', img)
        k = cv2.waitKey(1)
        if k in [ord(x) for x in ['e', 'w', 'n', 's']]:
            enter_lane_set[chr(k)] = [start_x, start_y, end_x, end_y]
            if k == ord('e'):
                print("东进口道检测线已设置")
            elif k == ord('w'):
                print("西进口道检测线已设置")
            elif k == ord('n'):
                print("北进口道检测线已设置")
            elif k == ord('s'):
                print("南出口道检测线已设置")
        if k in [ord(x) for x in ['E', 'W', 'N', 'S']]:
            exit_lane_set[chr(k)] = [start_x, start_y, end_x, end_y]
            if k == ord('E'):
                print("东出口道检测线已设置")
            elif k == ord('W'):
                print("西出口道检测线已设置")
            elif k == ord('N'):
                print("北出口道检测线已设置")
            elif k == ord('S'):
                print("南出口道检测线已设置")
        if k == ord('q'):
            break
    # 视频要压缩检测线对应缩短
    for lane_set in [enter_lane_set, exit_lane_set]:
        for key in lane_set:
            lane_set[key][0] = int(lane_set[key][0] * (960 / width))
            lane_set[key][1] = int(lane_set[key][1] * (960 / width))
            lane_set[key][2] = int(lane_set[key][2] * (540 / height))
            lane_set[key][3] = int(lane_set[key][3] * (540 / height))
    cv2.destroyAllWindows()
    # --------------------------------------创建存储检测数据的数据结构
    '''每条检测线有一个通过的车辆的哈希表，入口道检测线的哈希表存储驶入交叉口的车辆；出口道检测线的哈希表存储驶出交叉口的车辆
       当一条入口道检测线A第一次与车辆检测框相交时，A的哈希表中添加此车辆
       当一条出口道检测线B第一次与车辆检测框相交时，遍历所有入口道哈希表找到该车辆的驶入入口道C，C的哈希表中删去此车辆，C-B流向流量 + 1
       当车辆驶出检测区域时遍历所有驶出哈希表删除该车辆'''
    enter_set_dict = {}  # 入口道检测线驶入车辆集合的哈希表
    exit_set_dict = {}  # 出口道检测线驶出车辆集合的哈希表
    count = {}  # 各流向流量表，key为：入口道+出口道
    enter_count = {}  # 入口道流量
    for enter in enter_lane_set.keys():
        enter_count[enter] = 0
        enter_set_dict[enter] = set()
        exit_set_dict[enter] = set()
        for ex in enter_lane_set.keys():
            count[enter + ex] = 0
    # -----------------------------------------图像处理
    # 创建检测器
    detector = Detector()

    while True:
        # 读取每帧图片
        _, im = capture.read()
        if im is None:
            break

        # 缩小尺寸，1920x1080->960x540
        im = cv2.resize(im, (960, 540))
        # --------------------------------------------检测、追踪、流量统计
        # 检测当前帧
        bboxes = detector.detect(im)
        # 画出追踪框和更新流量数据
        output_image_frame = im
        bbox_ls = []
        if len(bboxes) > 0:
            # 追踪器更新
            bbox_ls = tracker.update(bboxes, im)
            # 流量更新
            for bbox in bbox_ls:
                cx1, cy1, cx2, cy2, label, track_id = bbox
                car_box = [cx1, cy1, cx2, cy2]
                # 判断车辆是否第一次越过检测线并获取车辆驶入进口道id
                ret, lane_id = get_enter_lane()
                if ret:
                    enter_set_dict[lane_id].add(str(track_id))
                    enter_count[lane_id] = enter_count[lane_id] + 1
                    break
        # ---------------------------------------将检测、追踪、流量统计信息写入图片
        # 图中画出检测线
        for lane_set in [enter_lane_set, exit_lane_set]:
            for line in lane_set.values():
                cv2.line(im, (line[0], line[1]), (line[2], line[3]),
                         (0, 0, 255), 5)
        # 画出检测和追踪结果画框
        output_image_frame = tracker.draw_bboxes(im, bbox_ls, line_thickness=None)
        # 将流量数据写入图片
        text_draw = ''
        for lane_id, count in enter_count.items():
            text_draw = text_draw + lane_id + ": " + str(count) + "   "
        output_image_frame = cv2.putText(img=output_image_frame, text=text_draw,
                                         org=(int(960 * 0.01), int(540 * 0.05)),
                                         fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                         fontScale=1, color=(0, 0, 255), thickness=2)
        # 实时展示处理结果
        cv2.imshow('demo', output_image_frame)
        cv2.waitKey(1)
    # 释放资源
    capture.release()
    cv2.destroyAllWindows()
