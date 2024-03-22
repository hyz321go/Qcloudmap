from PyQt5 import QtCore, QtGui, QtWidgets
from qgis.PyQt.QtWidgets import QDialog, QHBoxLayout, QDockWidget, QVBoxLayout, QDesktopWidget, QMessageBox
# 导入PyQt5和QGIS PyQt模块中的相关类。

from qgis.core import QgsVectorLayerCache, QgsVectorLayer
# 导入QGIS的核心库中有关矢量图层缓存和矢量图层的类。

from qgis.gui import QgsAttributeTableView, QgsAttributeTableModel, QgsAttributeTableFilterModel, QgsGui


# 导入QGIS的图形用户界面库中有关属性表的视图、模型、过滤模型的类以及通用的GUI组件。

class AttributeDialog(QDialog):
    # 定义属性对话框类，它继承自QDialog类。

    def __init__(self, mainWindows, layer):
        # 类初始化方法，接收主窗口对象和图层对象作为参数。
        # mainWindows: MainWindow
        super(AttributeDialog, self).__init__(mainWindows)
        # 调用父类的构造函数。
        self.mainWindows = mainWindows
        # 将传入的主窗口对象赋值给self.mainWindows。
        self.mapCanvas = self.mainWindows.mapCanvas
        # 从主窗口对象中获取地图画布对象。
        self.layer: QgsVectorLayer = layer
        # 将传入的图层对象赋值给self.layer，它是一个QgsVectorLayer类型的矢量图层。
        self.setObjectName("attrWidget" + self.layer.id())
        # 设置对象的名称，名称是"attrWidget"后跟图层的ID。
        self.setWindowTitle("属性表:" + self.layer.name())
        # 设置窗口的标题，标题为"属性表:"后跟图层的名称。

        vl = QHBoxLayout(self)
        # 创建一个水平布局管理器。
        self.tableView = QgsAttributeTableView(self)
        # 创建一个属性表视图对象。
        self.resize(800, 600)
        # 设置属性对话框的大小为800x600像素。
        vl.addWidget(self.tableView)
        # 将属性表视图添加到水平布局管理器。

        self.center()
        # 调用center()方法，将对话框移动到屏幕中央。
        self.openAttributeDialog()
        # 调用openAttributeDialog()方法，初始化和加载属性对话框中用于显示属性的模型。
        QgsGui.editorWidgetRegistry().initEditors(self.mapCanvas)
        # 通过QGIS GUI组件库来初始化编辑器小部件。

    def center(self):
        # center()方法：用于计算并设置属性对话框显示在屏幕中央的位置。
        # 获取屏幕的尺寸信息。
        screen = QDesktopWidget().screenGeometry()
        # 获取窗口的尺寸信息。
        size = self.geometry()
        # 将窗口移动到屏幕居中的位置。
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)

    def openAttributeDialog(self):
        # openAttributeDialog()方法: 初始化并显示属性表。
        # iface是一个全局对象，用于访问QGIS接口，此处未使用。
        # 上面的注释"iface"指的是在QGIS插件开发中，iface是常用的代表QGIS界面的全局对象。

        self.layerCache = QgsVectorLayerCache(self.layer, 10000)
        # 创建一个属性表模型的缓存，缓存10000条要素。
        self.tableModel = QgsAttributeTableModel(self.layerCache)
        # 根据缓存创建属性表模型。
        self.tableModel.loadLayer()
        # 加载图层数据到模型。

        self.tableFilterModel = QgsAttributeTableFilterModel(self.mapCanvas, self.tableModel, parent=self.tableModel)
        # 创建一个属性表的过滤模型，用于处理属性表的显示方式。
        self.tableFilterModel.setFilterMode(QgsAttributeTableFilterModel.ShowAll)  # 显示问题
        # 设置过滤模型以显示所有属性数据。
        self.tableView.setModel(self.tableFilterModel)
        # 设置属性表视图的模型为过滤后的模型。
        # 被注释掉的"self.tableView.edit()"和下一行的print语句，它们先前的功能可能是用于编辑模式及调试，但在此已经不需要。