from qgis.PyQt import QtCore  # 导入 QtCore 模块，用于处理事件和信号
from qgis.core import QgsApplication  # 导入 QgsApplication 类，用于管理 QGIS 应用程序
from PyQt5.QtCore import Qt  # 导入 Qt 模块，用于设置应用程序的属性
import os  # 导入 os 模块，用于操作文件系统路径
import traceback  # 导入 traceback 模块，用于捕获和打印异常信息
from mainWindow import MainWindow  # 导入自定义的 MainWindow 类，用于创建应用程序的主窗口

if __name__ == '__main__':
    QgsApplication.setPrefixPath('C:/qgis322/apps/qgis-ltr', True)  # 设置 QGIS 应用程序的安装路径
    QgsApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  # 启用高 DPI 缩放功能，确保在高分辨率屏幕上显示正确
    app = QgsApplication([], True)  # 创建 QgsApplication 实例对象，参数表示不使用图形界面

    t = QtCore.QTranslator()  # 创建翻译器对象
    t.load(r'.\zh-Hans.qm')  # 加载中文翻译文件
    app.installTranslator(t)  # 安装翻译器，用于国际化界面

    app.initQgis()  # 初始化 QGIS 应用程序，包括加载插件、设置环境变量等

    mainWindow = MainWindow()  # 创建主窗口对象
    mainWindow.show()  # 显示主窗口

    # 以下是添加图层的示例代码，被注释掉了
    # shp = r"D:\111.shp"
    # tif = r"D:\test.tif"
    # mainWindow.addVectorLayer(shp)  # 添加矢量图层
    # mainWindow.addRasterLayer(tif)  # 添加栅格图层

    app.exec_()  # 执行应用程序的事件循环，使程序进入消息循环状态，等待用户操作

    app.exitQgis()  # 退出 QGIS 应用程序，释放资源并关闭应用程序
