from sahi.predict import get_sliced_prediction

from detector import Detector

import tracker
import cv2

import os

from sahi import AutoDetectionModel
import time

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
    global track_id
    # 检测当前车辆是否越过集合中的检测线
    for line_id, line_pos in lane_set.items():
        lx1, ly1, lx2, ly2 = line_pos
        global car_box
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


# ----------------------------- 画检测线
def draw_detect_line():
    # 初始化检测线---> 得到检测线坐标集合 enter_lane_set
    print("开始画检测线")
    print('''鼠标点击检测线起点，拖至检测线重点松开
       画好检测线后，按下e w s n来表示这条检测线是东 西 南 北哪个方向的检测线，小写字母表示入口道，大写字母表示出口道
       当画完所有检测线时按 s 退出''')
    # 创建鼠标点击事件：点击和松开时将坐标赋予 start_x, start_y, end_x, end_y
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    cv2.setMouseCallback('image', draw_line)
    global enter_lane_set  # 入口道检测线坐标集合
    global exit_lane_set  # 出口道检测线坐标集合
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
            cv2.putText(img=img, text=rf"{chr(k)}",
                        org=(start_x + 2, int(start_y + 2)),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=1, color=(0, 255, 0), thickness=2)
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
            cv2.putText(img=img, text=rf"{chr(k)}",
                        org=(start_x + 2, int(start_y + 2)),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=1, color=(0, 255, 0), thickness=2)
        if k in [ord(x) for x in ['q', 'Q']]:
            break
    # 保存划线结果
    sava_path = rf"{out_path}/{file_name.split('.')[0]}"
    if not os.path.exists(sava_path):
        os.mkdir(sava_path)
    cv2.imwrite(sava_path + r"/detect_line.png", img)
    video_detect_line_dict[file_name] = [enter_lane_set, exit_lane_set]
    enter_lane_set = {}
    exit_lane_set = {}


def countFlow(video_path, use_sahi=False, save_video=True, show_video=False, use_uav=False):
    start_time = time.time()
    # -------------------------------------配置信息
    # use_sahi = False  # 是否使用 sahi 算法增强检测结果
    # save_video = True  # 是否存储检测视频
    # show_video = False  # 是否展示检测过程
    # video_path =  # 视频路径
    # use_uav=False  # 是否为无人机航拍视频

    if not os.path.exists(out_path):
        os.mkdir(out_path)

    sava_path = rf"{out_path}/{file_name.split('.')[0]}"
    excel_save_path = fr"{sava_path}\{file_name.split('/')[0]}.xlsx"
    output_video_path = rf'{sava_path}/{file_name.split("/")[0]}.avi'  # 指定输出视频文件
    # 权重文件路径
    if use_uav:
        weight_path = r'./weights/best-UAV-ROD.pt'
    else:
        weight_path = r'./weights/best-jiankong-800.pt'
    # -------------------------------------------读入并获取视频信息
    # 打开视频
    capture = cv2.VideoCapture(video_path)
    # 获取视频FPS和尺寸
    fps = capture.get(cv2.CAP_PROP_FPS)
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # 设置展示视频大小
    out_width = 1680
    out_height = int(out_width / width * height)
    # -----------------------------视频要压缩检测线对应缩短
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
    # ----------------------------------------- 创建检测器
    if use_sahi:
        detector = AutoDetectionModel.from_pretrained(
            model_type='yolov5',
            model_path=weight_path,
            config_path=r"models/yolov5x.yaml",
            confidence_threshold=0.2,
            device="cuda:0"
        )
    else:
        detector = Detector(weight_path)
    # ---------------------------- 创建视频输出对象
    # 定义输出视频编解码器
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    # 创建输出视频对象
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (out_width, out_height))
    # 记录当前处理帧数
    frame_count = 0
    # 记录当前处理是第几分钟
    minute = 0
    while True:
        frame_count += 1
        if frame_count % (fps * 60) == 0:
            minute += 1
            print(f"{minute}min已处理完毕")
            frame_count = 0
        # 读取每帧图片
        _, im = capture.read()
        if im is None:
            break

        # 缩小尺寸
        im = cv2.resize(im, (out_width, out_height))
        # --------------------------------------------检测、追踪、流量统计
        # 检测当前帧 -> 获得 bboxes（[x1, y1, x2, y2, clsID, conf]列表）
        if use_sahi:
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
        else:
            bboxes = detector.detect(im)
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
            global track_id
            for bbox in bbox_ls:
                cx1, cy1, cx2, cy2, label, track_id = bbox
                # 车辆还未驶出检测区域
                if track_id in remove_car_set:
                    remove_car_set.remove(track_id)
                global car_box
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
        if show_video or save_video:
            # 图中画出检测线
            for lane_set in [enter_lane_set, exit_lane_set]:
                for name, line in lane_set.items():
                    cv2.line(im, (line[0], line[1]), (line[2], line[3]),
                             (0, 0, 255), 5)
                    # 标记检测线名称
                    cv2.putText(img=output_image_frame, text=name,
                                org=(int(line[0]), int(line[1] + 0.1)),
                                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                fontScale=1, color=(0, 0, 255), thickness=2)
            # 画出检测和追踪结果画框
            output_image_frame = tracker.draw_bboxes(im, bbox_ls, line_thickness=None)
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
            if show_video:
                # 实时展示处理结果
                cv2.imshow('demo', output_image_frame)
                cv2.waitKey(1)
            if save_video:
                # 写入输出视频
                out.write(output_image_frame)
    # 释放资源
    capture.release()
    out.release()
    cv2.destroyAllWindows()
    # -------------------------------- 运行数据保存到本地
    import pandas as pd

    # 创建ExcelWriter对象
    writer = pd.ExcelWriter(excel_save_path, engine='xlsxwriter')
    # 写入进口道流量
    pd.DataFrame({"入口道流量": enter_count_dict}).to_excel(writer, sheet_name='入口道流量', index=True)
    # 写入各流向流量
    # 将流量流量字典转化内dataframe格式
    df_count = {}
    for enter in enter_lane_set.keys():
        df_count[enter] = tmp = {}
        for ex in exit_lane_set.keys():
            tmp[ex] = count_dict[enter + ex]
    pd.DataFrame(df_count).to_excel(writer, sheet_name='各流向流量', index=True)
    # 保存Excel文件
    writer.save()
    print(f"流量文件已保存到{excel_save_path}")

    if save_video:
        print(f"检测过程视频保存在{video_path}")

    end_time = time.time()
    print(f"{file_name}检测完毕，共花费{(end_time - start_time) / 60}分钟")

    # 视频相关数据保存
    t = open(rf'{sava_path}/readme.txt', 'w')
    t.write(f"视频名：{file_name};\n")
    t.write(rf"视频时长：{minute}分{frame_count / 60}秒;")


# ------------------- 全局变量
start_x, start_y, end_x, end_y = -1, -1, -1, -1
car_box = []
track_id = 0
enter_lane_set = {}
exit_lane_set = {}
# 存储各视频的检测线坐标
video_detect_line_dict = {}

if __name__ == '__main__':
    # path = r"F:\zhangBo\video\jiankong"
    path = r'F:\下载\test'
    out_path = rf'{path}/output'
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    # 为此路径下所有视频画检测线
    for file_name in os.listdir(path):
        if file_name.split('.')[-1] == 'mp4':
            # 读取视频
            capture = cv2.VideoCapture(rf'{path}/{file_name}')
            ret, img = capture.read(0)
            # 画检测线
            draw_detect_line()
    # 统计此路径下所有视频中的流量，并将数据保存在此路径的output文件夹中
    # 打开视频
    for file_name in os.listdir(path):
        if file_name.split('.')[-1] == 'mp4':
            # 检索当前视频的检测线坐标
            enter_lane_set, exit_lane_set = video_detect_line_dict[file_name]
            countFlow(rf'{path}/{file_name}')
