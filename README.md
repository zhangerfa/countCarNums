# countNumOfCars
实现监控视角、无人机航拍视角下的交叉口车流量统计，检测使用[yolov5](https://github.com/ultralytics/yolov5) ，追踪使用[deepSort](https://github.com/nwojke/deep_sort) ，小物体检测可选[sahi](https://github.com/obss/sahi) 算法对检测结果进行增强
<img src="output/count.gif">
### 训练数据
- 无人机航拍视角使用[UAV-ROD](https://github.com/fengkaibit/UAV-ROD) 数据，经过测试在大疆MiNi2拍摄下飞行高度100m内检测精度足够完成流量统计
- 位于制高点的道路监控视角使用自己标注的数据
### 使用方法
在main.py中对以下信息进行配置即可运行
```python
use_sahi = False  # 是否使用 sahi 算法增强检测结果
save_video = False  # 是否存储检测视频
show_video = True  # 是否展示检测过程
video_path = r'..\video\JinXinGuoJi.mp4'  # 视频路径
excel_save_path = r'..\video\data\JinXinGuoJi.xlsx'
output_path = r'../video/output/output.avi'  # 指定输出视频文件
weight_path = r'./weights/best-jiankong-800.pt'  # 权重文件路径
```
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
### 待做功能
- [x] 绘制检测线
- [x] 各流向流量统计
- [ ] 克服无人机镜头偏移造成的检测线偏移
- [ ] 速度抽样统计
