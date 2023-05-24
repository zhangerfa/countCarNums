# -*- coding: utf-8 -*-
# @Time : 2023/5/23 22:43
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal

from gui import login, register, main

import countFlow


class Login(QtWidgets.QMainWindow, login.Ui_MainWindow):
    show_register_signal = pyqtSignal()  # 该信号用于展示注册窗体
    show_main_signal = pyqtSignal()  # 该信号用于主页面窗体

    def __init__(self):
        super(Login, self).__init__()
        self.setupUi(self)

    # 显示注册页面
    def register(self):
        self.show_register_signal.emit()

    # 登录，验证账号和密码
    def login(self):
        if self.username.text() == 'hkqd' and self.password.text() == '123456':
            self.close()
            self.show_main_signal.emit()
        else:
            print("密码错误")


class Register(QtWidgets.QMainWindow, register.Ui_MainWindow):
    show_login_signal = pyqtSignal()  # 该信号用于展示登录窗体

    def __init__(self):
        super(Register, self).__init__()
        self.setupUi(self)

    def login(self):
        self.close()
        registerUi.show()

    def login(self):
        self.show_login_signal.emit()


class Main(QtWidgets.QMainWindow, main.Ui_MainWindow):
    select_path_signal = pyqtSignal()  # 选择视频路径信号

    def __init__(self):
        super(Main, self).__init__()
        self.setupUi(self)

        self.path = None  # 视频文件夹路径
        self.use_sahi = False  # 是否使用sahi算法
        self.show_video = False  # 是否显示视频
        self.sava_video = False  # 是否保存视频
        self.is_uav = False  # 是否为无人机航拍视频

    def selectFile(self):
        # 用户选择文件夹
        self.select_path_signal.emit()

    def selectSavePath(self):
        # 用户选择保存路径
        self.select_path_signal.emit()

    def useSahi(self):
        pass

    def change_if_show_video(self):
        self.show_video = self.show_video_box.isChecked()

    def change_if_save_video(self):
        self.sava_video = self.save_video_box.isChecked()

    def change_if_uav(self):
        self.is_uav = self.video_type_box.isChecked()

    def start(self):
        # 开始检测
        print("开始检测")
        countFlow.start(self.path, None, self.use_sahi, self.show_video, self.sava_video, self.is_uav)


# 点击注册后关闭登录窗体，展示注册窗体
def show_register():
    loginUi.close()
    registerUi.show()


# 点击登录后关闭注册窗体，展示登录窗体
def show_login():
    registerUi.close()
    loginUi.show()


# 登录成功后跳转主页面
def show_main():
    loginUi.close()
    mainUi.show()


def select_path():
    path = QFileDialog.getExistingDirectory(None, "选取文件夹", "C:/")
    mainUi.pathText.setText(path)
    mainUi.path = path


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication, QFileDialog

    # 创建窗口对象
    app = QApplication(sys.argv)
    loginUi = Login()
    registerUi = Register()
    mainUi = Main()

    # 为窗口对象的组件绑定槽函数
    loginUi.show_register_signal.connect(show_register)
    loginUi.show_main_signal.connect(show_main)
    registerUi.show_login_signal.connect(show_login)
    mainUi.select_path_signal.connect(select_path)

    # 展示登录窗口
    mainUi.show()
    sys.exit(app.exec_())
