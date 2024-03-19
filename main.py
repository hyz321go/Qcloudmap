# 从qgis.PyQt导入所需的模块
from qgis.PyQt import QtCore
# 导入QGS应用程序接口
from qgis.core import QgsApplication
# 从PyQt5.QtCore导入Qt模块
# noinspection PyUnresolvedReferences
from PyQt5.QtCore import Qt
import os
import traceback
# 导入自定义的MainWindow类
from mainWindow import MainWindow

# PyQGIS的脚本的入口点，设置QGIS应用程序，并实例化主窗口
if __name__ == '__main__':
    # 设置QGIS应用程序的前缀路径，这是QGIS安装的位置
    QgsApplication.setPrefixPath('C:/qgis322/apps/qgis-ltr', True)
    # 启用高DPI缩放，用于支持高DPI的屏幕
    QgsApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # 创建一个QGS应用程序实例
    app = QgsApplication([], True)

    # 汉化菜单"Group Select"
    t = QtCore.QTranslator()
    t.load(r'.\zh-Hans.qm')
    app.installTranslator(t)

    # 初始化QGIS应用程序的资源
    app.initQgis()

    # 创建主窗口实例
    mainWindow = MainWindow()
    # 显示主窗口
    mainWindow.show()
    # 下面是加载栅格层和矢量层的示例代码，当前被注释掉了
    # tif = r"G:\QGIS\myData\ca_nrc_CGG2013an83.tif"
    # mainWindow.addRasterLayer(tif)

    # 加载一个矢量层，路径根据实际文件位置填写
    shp = r"G:\QGIS\myData\naturalearth_lowres.shp"
    mainWindow.addVectorLayer(shp)

    # 运行QGS应用程序
    app.exec_()
    # 退出时清理QGIS应用程序的资源
    app.exitQgis()
