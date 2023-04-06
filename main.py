from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction

import tracker
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
# 获取车辆是否第一次越过集合中的检测线及第一次越过的检测线id，返回值(是否第一次越过检测线, 第一次越过检测线的id)
#   如果车辆越过检测线
#       第一次越过检测线，返回(True, 当前越过检测线id)；
#       非第一次越过检测线，则找到其第一次越过的检测线id的检测线id，返回(False, 第一次越过检测线id)
#   如果未越过检测线返回(False, None)
#
# enter_lane_set: 检测线起讫点坐标（x1 y1 x2 y2）
# car_box: 车辆检测框左上和右下坐标（x1 y1 x2 y2）
def get_first_lane(lane_set, car_set_dict):
    # 检测当前车辆是否越过集合中的检测线
    for line_id, line_pos in lane_set.items():
        lx1, ly1, lx2, ly2 = line_pos
        if check_intersect((lx1, ly1), (lx2, ly2), car_box):
            # 当车辆越过一条检测线时，判断该车辆之前是否已越过该检测线
            if track_id in car_set_dict[line_id]:
                return False, line_id
            return True, line_id
    # 当车辆不和集合中任何检测线相交时判断该车辆之前是否已近越过集合中任意检测线
    for line_id, car_set in car_set_dict.items():
        if track_id in car_set:
            return False, line_id
    # 车辆从未越过集合中的检测线
    return False, None


if __name__ == '__main__':
    # -------------------------------------------读入并获取视频信息
    # 打开视频
    video_path = r'..\video\222.mp4'
    capture = cv2.VideoCapture(video_path)
    # 指定输出视频文件
    output_path = r'../video/output/output.avi'
    # 获取视频FPS和尺寸
    fps = capture.get(cv2.CAP_PROP_FPS)
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # 设置输出视频大小
    out_width = 1680
    out_height = int(out_width / width * height)
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
        if k in [ord(x) for x in ['q', 'Q']]:
            break
    # 视频要压缩检测线对应缩短
    for lane_set in [enter_lane_set, exit_lane_set]:
        for key in lane_set:
            lane_set[key][0] = int(lane_set[key][0] * (out_width / width))
            lane_set[key][1] = int(lane_set[key][1] * (out_width / width))
            lane_set[key][2] = int(lane_set[key][2] * (out_height / height))
            lane_set[key][3] = int(lane_set[key][3] * (out_height / height))
    cv2.destroyAllWindows()
    # --------------------------------------创建存储检测数据的数据结构
    '''每条检测线有一个通过的车辆的哈希表，入口道检测线的哈希表存储驶入交叉口的车辆；出口道检测线的哈希表存储驶出交叉口的车辆
       当一条入口道检测线A第一次与车辆检测框相交时，A的哈希表中添加此车辆
       当一条出口道检测线B第一次与车辆检测框相交时，遍历所有入口道哈希表找到该车辆的驶入入口道C，C的哈希表中删去此车辆，C-B流向流量 + 1
       当车辆驶出检测区域时遍历所有驶出哈希表删除该车辆'''
    enter_car_set_dict = {}  # 入口道检测线驶入车辆集合的哈希表
    exit_car_set_dict = {}  # 出口道检测线驶出车辆集合的哈希表
    count_dict = {}  # 各流向流量表，key为：入口道+出口道
    enter_count_dict = {}  # 入口道流量
    for enter in enter_lane_set.keys():
        enter_count_dict[enter] = 0
        enter_car_set_dict[enter] = set()
        for ex in exit_lane_set.keys():
            exit_car_set_dict[ex] = set()
            count_dict[enter + ex] = 0
    # -----------------------------------------图像处理
    # 创建检测器
    # detector = Detector()
    # 建立检测对象
    detector = AutoDetectionModel.from_pretrained(
        model_type='yolov5',
        model_path=r"weights/yolov5x.pt",
        config_path=r"weights/yolov5x.yaml",
        confidence_threshold=0.2,
        device="cuda:0"
    )
    # 定义输出视频编解码器
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    # 创建输出视频对象
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    # 处理图片
    while True:
        # 读取每帧图片
        _, im = capture.read()
        if im is None:
            break

        # 缩小尺寸
        im = cv2.resize(im, (out_width, out_height))
        # --------------------------------------------检测、追踪、流量统计
        # 检测当前帧
        result = get_sliced_prediction(
            im,
            detector,
            slice_height=200,
            slice_width=200,
            overlap_height_ratio=0.2,
            overlap_width_ratio=0.2
        )
        # 将sahi检测结果转换为[x1, y1, x2, y2, clsID, conf]格式
        bboxes = []
        for x in result.object_prediction_list:
            voc_bbox = x.bbox.to_voc_bbox()
            voc_bbox.append(x.category.id)
            voc_bbox.append(x.score.value)
            bboxes.append(voc_bbox)
        # 不需要再存储的车辆集合，初始值为所有检测线记录的车辆集合的交集
        # 当当前帧中出现一辆车时从该集合中删去该车，最终剩下的车辆从检测线记录的车辆集合中删除
        remove_car_set = set()
        for car_set_dict in [enter_car_set_dict, exit_car_set_dict]:
            for car_set in car_set_dict.values():
                remove_car_set = remove_car_set.union(car_set)
        # 画出追踪框和更新流量数据
        output_image_frame = im
        bbox_ls = []
        if len(bboxes) > 0:
            # 追踪器更新
            bbox_ls = tracker.update(bboxes, im)
            # 流量更新
            for bbox in bbox_ls:
                cx1, cy1, cx2, cy2, label, track_id = bbox
                # 车辆还未驶出检测区域
                if track_id in remove_car_set:
                    remove_car_set.remove(track_id)
                car_box = [cx1, cy1, cx2, cy2]
                # 车辆第一次越过入口道则将其加入该入口道的哈希表，该入口道流量 + 1
                # 车辆非第一次越过入口道则判断其是否第一次越过出口道，是则其驶入入口道哈希表中删去此车辆，该流向流量 + 1
                ret, lane_id = get_first_lane(enter_lane_set, enter_car_set_dict)  # 返回(是否第一次越过入口道， 第一次越过入口道的id)
                if ret:
                    # 第一次越过入口道
                    enter_car_set_dict[lane_id].add(track_id)
                    enter_count_dict[lane_id] = enter_count_dict[lane_id] + 1
                elif lane_id is not None:
                    # 非第一次越过入口道
                    ret, exit_lane_id = get_first_lane(exit_lane_set, exit_car_set_dict)
                    if ret:
                        # 第一次越过出口道
                        exit_car_set_dict[exit_lane_id].add(track_id)
                        count_dict[lane_id + exit_lane_id] = count_dict[lane_id + exit_lane_id] + 1
        # 删去所有已驶出检测区域的车辆
        for car_set_dict in [enter_car_set_dict, exit_car_set_dict]:
            for car_set in car_set_dict.values():
                for remove_id in remove_car_set:
                    if remove_id in car_set:
                        car_set.remove(remove_id)
        # ---------------------------------------将检测、追踪、流量统计信息写入图片
        # 图中画出检测线
        for lane_set in [enter_lane_set, exit_lane_set]:
            for line in lane_set.values():
                cv2.line(im, (line[0], line[1]), (line[2], line[3]),
                         (0, 0, 255), 5)
        # 画出检测和追踪结果画框
        # output_image_frame = tracker.draw_bboxes(im, bbox_ls, line_thickness=None)

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

            if cls.id == 2:
                cv2.rectangle(output_image_frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
        # 将流量数据写入图片
        i = 0
        text_count = 0
        text_draw = ''
        for count_dict in [enter_count_dict, count_dict]:
            for lane_id, c in count_dict.items():
                text_draw = text_draw + lane_id + ": " + str(c) + "   "
                text_count = text_count + 1
                if text_count % 4 == 0:
                    output_image_frame = cv2.putText(img=output_image_frame, text=text_draw,
                                                     org=(int(out_width * 0.01), int(out_height * 0.05 * (i + 1))),
                                                     fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                                     fontScale=1, color=(0, 0, 255), thickness=2)
                    i = i + 1
                    text_draw = ''
        if text_count % 4 != 0:
            output_image_frame = cv2.putText(img=output_image_frame, text=text_draw,
                                             org=(int(out_width * 0.01), int(out_height * 0.05 * (i + 1))),
                                             fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                             fontScale=1, color=(0, 0, 255), thickness=2)
        # 实时展示处理结果
        cv2.imshow('demo', output_image_frame)
        cv2.waitKey(1000)
        # 写入输出视频
        # out.write(output_image_frame)
    # 释放资源
    capture.release()
    out.release()
    cv2.destroyAllWindows()
