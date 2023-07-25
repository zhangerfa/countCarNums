import matplotlib.pyplot as plt
from matplotlib.patches import Arrow
import numpy as np
from scipy.interpolate import interp1d

# 路口类
class Intersection:
    def __init__(self, enter_ls, exit_ls, name, color_dict=None):
        # enter_ls: 入口道列表
        # exit_ls: 出口道列表
        # name: 路口名称
        self.enter_ls = enter_ls
        self.exit_ls = exit_ls
        self.name = name
        if color_dict is None:
            self.color_dict = {"南": "red",
                               "北": "blue",
                               "西": "green",
                               "东": "purple"}
        else:
            self.color_dict = color_dict

    def draw_flow(self):
        # 设置各入口道和出口道的坐标
        self.set_point()
        # 流量和线宽换算系数
        da = 100
        flow_front_size = 12 # 流量标注字体大小
        # 画出各流向流量
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        plt.figure(figsize=(10, 10))
        for enter in self.enter_ls:
            for (exit, flow) in enter.flow_dict.items():
                # 画出流向流量：流量越大，线条越粗，相同进口道流出流量颜色相同
                plt.plot([enter.x, exit.x], [enter.y, exit.y],
                         color=enter.color, linewidth=flow / da)
                # 标出流量
                dx = 0.1 if enter.x == exit.x else -0.5 if enter.x > exit.x else 0.5
                dy = 0.1 if enter.y == exit.y else -0.5 if enter.y > exit.y else 0.5
                plt.text(enter.x + dx, enter.y + dy, str(flow),
                         fontsize=flow_front_size)
        # 画入口道总流量
        for enter in self.enter_ls:
            if enter.flow == 0:
                continue
            plt.plot([enter.x, enter.x + enter.off[0] * 0.9],
                     [enter.y, enter.y + enter.off[1] * 0.9],
                        color=enter.color, linewidth=enter.flow / da)
            # 标出流量
            dx = 0.1 if enter.off[0] == 0 else 0
            dy = 0.1 if enter.off[1] == 0 else 0
            plt.text(enter.x + dx, enter.y + dy,
                     str(enter.flow), fontsize=flow_front_size)
        # 画出口道总流量
        for exit in self.exit_ls:
            if exit.flow == 0:
                continue
            plt.annotate('', xy=(exit.x + exit.off[0], exit.y + exit.off[1]),
                         xytext=(exit.x, exit.y),
                         arrowprops=dict(color=exit.color,
                                         width=exit.flow / da,
                                         headwidth=exit.flow / da * 2))
            dx = 0.1 if exit.off[0] == 0 else 0
            dy = 0.1 if exit.off[1] == 0 else 0
            plt.text(exit.x + dx, exit.y + dy,
                     str(exit.flow), fontsize=flow_front_size)

        # 标出总流量
        plt.text(3, -3, f"{self.get_flow()}cpu/h", color="red", fontsize=15)
        # 标出路口名称
        for enter in self.enter_ls:
            if "东" in enter.name or "西" in enter.name:
                plt.text(enter.x + 2 * enter.off[0],
                         enter.y + 2 * enter.off[1],
                         enter.name, fontsize=15, rotation=90)
            else:
                plt.text(enter.x + 2 * enter.off[0],
                     enter.y + 2 * enter.off[1],
                     enter.name, fontsize=15)
        # 隐藏坐标轴
        plt.axis('off')
        # 设置标题
        plt.title(self.name)
        plt.show()

    # 计算路口总流量
    def get_flow(self):
        return sum([enter.flow for enter in self.enter_ls])

    # 设置各入口道和出口道的坐标
    def set_point(self):
        for enter in self.enter_ls:
            if "南" in enter.name:
                enter.x = 1
                enter.y = -3
                enter.off = [0, -1]
                enter.color = self.color_dict["南"]
            elif "北" in enter.name:
                enter.x = -1
                enter.y = 3
                enter.off = [0, 1]
                enter.color = self.color_dict["北"]
            elif "西" in enter.name:
                enter.x = -3
                enter.y = -1
                enter.off = [-1, 0]
                enter.color = self.color_dict["西"]
            elif "东" in enter.name:
                enter.x = 3
                enter.y = 1
                enter.off = [1, 0]
                enter.color = self.color_dict["东"]
            else:
                throw(f"入口道名称请包含方向信息，当前入口道名称：{enter.name}")
        for exit in self.exit_ls:
            if "南" in exit.name:
                exit.x = -1
                exit.y = -3
                exit.off = [0, -1]
                exit.color = self.color_dict["南"]
            elif "北" in exit.name:
                exit.x = 1
                exit.y = 3
                exit.off = [0, 1]
                exit.color = self.color_dict["北"]
            elif "西" in exit.name:
                exit.x = -3
                exit.y = 1
                exit.off = [-1, 0]
                exit.color = self.color_dict["西"]
            elif "东" in exit.name:
                exit.x = 3
                exit.y = -1
                exit.off = [1, 0]
                exit.color = self.color_dict["东"]
            else:
                throw(f"出口道名称请包含方向信息，当前出口道名称：{exit.name}")


# 抽象点类
class Point:
    def __init__(self, name, type):
        # x, y: 坐标
        # name: 名称
        self.x = 0
        self.y = 0
        self.name = name
        self.flow = 0  # 总流量
        self.flow_dict = {}  # 与之相连的节点及对应流量
        self.type = type  # 类型
        self.color = None  # 颜色
        self.off = []  # 画该节点总流量时由节点坐标推出总流量坐标的偏移量
        self.flow = 0  # 路口总流量

    def __hash__(self):
        return hash((self.name, self.x, self.y))

# 获取路口对象的工厂方法
def intersection_factory(flow_dict, name="路口", color_dict=None):
    # flow_dict: 流量字典 {入口道名称: {出口道名称: 流量, ...}, ...
    # 由流量流向表创建入口道对象和出口道对象列表，并建立各入口道和出口道之间流向关系
    enter_ls = []
    exit_ls = []
    exit_name_dict = {}
    for enter_name, exit_dict in flow_dict.items():
        enter = Point(enter_name, "enter")
        enter_ls.append(enter)
        for exit_name, flow in exit_dict.items():
            if exit_name in exit_name_dict:
                exit = exit_name_dict[exit_name]
            else:
                exit = Point(exit_name, "exit")
                exit_ls.append(exit)
                exit_name_dict[exit_name] = exit
            enter.flow_dict[exit] = exit.flow_dict[enter] = flow
    # 统计各入口道和出口道的总流量
    for enter in enter_ls:
        enter.flow = sum(enter.flow_dict.values())
    for exit in exit_ls:
        exit.flow = sum(exit.flow_dict.values())
    # 创建路口对象
    intersection = Intersection(enter_ls, exit_ls, name=name, color_dict=color_dict)
    return intersection