# countNumOfCars
实现监控视角、无人机航拍视角下的交叉口车流量统计，检测使用[yolov5](https://github.com/ultralytics/yolov5) ，追踪使用[deepSort](https://github.com/nwojke/deep_sort) ，小物体检测可选[sahi](https://github.com/obss/sahi) 算法对检测结果进行增强
### 航拍视频检测
<img src="output/uav.gif">

### 监控视频批量检测
<img src="output/monitor.gif"/>

### 训练数据
- 无人机航拍视角使用[UAV-ROD](https://github.com/fengkaibit/UAV-ROD) 数据，经过测试在大疆MiNi2拍摄下飞行高度100m内检测精度足够完成流量统计
- 位于制高点的道路监控视角使用自己标注的数据，只标注了800张就基本够用
## 使用方法
### 安装依赖
使用conda
```commandline
conda install --yes --file requirements.txt
```
使用pip
```commandline
pip install -r requirements.txt
```
本地运行环境中主要依赖版本如下：
```text
pytorch-cuda = 11.7
torchvision = 0.14.0
cuda = 11.7
```
### 主要函数
本程序包含两个主要函数：`draw_detect_line()`和`countFlow()`，分别用来画检测线和流量统计，均在在main.py中。

其中`draw_detect_line()`需要传入待画检测线视频的路径，检测线画完后以`dict`存储视频名和存储检测线坐标数据；

```python
def draw_detect_line(video_path):
  pass
  # video_path =  # 视频路径  
```

在运行`countFlow()`时需要传入待统计流量的视频路径（该视频必须已画检测线，否则缺少检测线数据），其他入参看下方介绍，运行结束可以得到检测视频、流量excel表、检测线位置及名称的png图，被检测视频的基本信息的txt文件
```python
def countFlow(video_path, use_sahi=False, save_video=True, show_video=False, use_uav=False):
  pass
  # video_path =  # 视频路径    
  # use_sahi = False  # 是否使用 sahi 算法增强检测结果
  # save_video = True  # 是否存储检测视频
  # show_video = False  # 是否展示检测过程
  # use_uav=False  # 是否为无人机航拍视频
```

使用这两个函数即可完成视频流量统计
### 批量统计同一路径下的视频中的流量
先未路径下所有视频画检测线，后统计流量；
- 以下代码中仅保证检测mp4格式视频，如果视频包含其他格式请自行添加
```python
import os

# 带处理的视频所在路径
path = r"..\video\jiankong"
# 运行结果保存路径
out_path = rf'{path}/output'
if not os.path.exists(out_path):
    os.mkdir(out_path)
# 为此路径下所有视频画检测线
for file_name in os.listdir(path):
    if file_name.split('.')[-1] == 'mp4':
        # 画检测线
        draw_detect_line(rf'{path}/{file_name}')
# 统计此路径下所有视频中的流量，并将数据保存在此路径的output文件夹中
# 打开视频
for file_name in os.listdir(path):
    if file_name.split('.')[-1] == 'mp4':
        # 检索当前视频的检测线坐标
        enter_lane_set, exit_lane_set = video_detect_line_dict[file_name]
        countFlow(rf'{path}/{file_name}', show_video=True)
```

程序运行之后为路径下的所有视频画出检测线：
- 当弹出图片时，在图中画出检测线：
  - 鼠标点击检测线一端不放拖至另一端松手即画完一条检测线
  - 检测线画完之后通过按键盘字母为检测线命名
  - 当检测区域为交叉口时，小写字母为入口道、大写字母为出口道
  - 当画完当前图片所有检测线时，按q结束

所有图片检测线画完后等待程序运行结束，默认会在图片路径下创建output文件夹用来保存运行结果
- 在output文件夹下有所有检测视频同名的文件夹，其中存放该视频的检测数据
  - 检测视频（运行时可选是否保存）
  - 入口道流量表和入口道到出口道的流向流量表
  - detect_line.png -- 用来保存检测线位置及名称
  
    <img src = "output/detect_line.png"/>
  - readme.txt -- 用于保存检测视频基本信息，目前有视频名称和时长

### 文件结构
```text
countNumOfCarsTrain  -- 训练数据处理和算法测试的辅助代码
data  -- 存放yolov5训练数据的路径
deep_sort  -- deep—_sort算法源码
models  --  yolov5源码
output -- 存放展示图片
runs  --  yolov5训练数据存放路径
sahi  --  sahi算法源码
utils  --  yolov5工具类
weights  --  权重文件存放路径

main.py  --  主程序
detector.py  --  封装了yolov5模型的创建和使用
tracker.py  --  封装了deep_sort模型的创建和使用
-- yolov5训练代码
train.py
val.py
```
## 待做功能
- [x] 绘制检测线
- [x] 各流向流量统计
- [x] 统计同一路径下所有视频中的流量数据
- [ ] 克服无人机镜头偏移造成的检测线偏移
- [ ] 速度抽样统计
