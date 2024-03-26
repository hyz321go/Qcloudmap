from ui.mapToolInputAttr import Ui_Dialog
from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import QMenu, QAction,QDesktopWidget,QDialog,QColorDialog,QMessageBox,QSizePolicy,QDockWidget,QLineEdit
from PyQt5.QtGui import QColor
from qgis.core import QgsLayerTreeNode, QgsLayerTree, QgsMapLayerType,\
    QgsVectorLayer, QgsProject,QgsMarkerSymbol,QgsFillSymbol,QgsLineSymbol,\
    QgsFeatureRenderer,QgsSingleSymbolRenderer,QgsApplication,QgsSimpleLineSymbolLayer,\
    QgsRasterLayer,QgsTaskManager, QgsMessageLog,QgsProcessingAlgRunnerTask, QgsApplication,\
    QgsProcessingContext, QgsProcessingFeedback,QgsProject,QgsTask,Qgis,QgsColorRampShader,QgsPalettedRasterRenderer,\
    QgsRasterShader,QgsSingleBandPseudoColorRenderer,QgsFeature,QgsGeometry,QgsPointXY

PROJECT = QgsProject.instance()


class inputAttrWindowClass(QDialog, Ui_Dialog):  # 继承了QDialog，Ui_Dialog两个类，即这是一个Qt对话框
    def __init__(self, mapTool, feat, mainWindow):  # 初始化类，并接受地图工具、特性（可能是地图的某一部分，如线、面等）、主窗口作为参数
        super(inputAttrWindowClass, self).__init__(mainWindow)  # 使用主窗口初始化父类
        self.setupUi(self)  # 设定UI，此函数应在Ui_Dialog定义
        self.mapTool = mapTool  # 地图工具
        self.feat: QgsFeature = feat  # 特性
        self.mainWindow = mainWindow  # 主窗口
        self.initUI()  # 初始化UI
        self.connectFunc()  # 连接一些函数，如与按钮点击事件相关的函数
        self.center()  # 将窗口中心化

    def center(self):  # 窗口中心化
        screen = QDesktopWidget().screenGeometry()  # 获取屏幕的尺寸信息
        size = self.geometry()  # 获取窗口的尺寸信息
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)  # 将窗口移动到指定位置

    def closeEvent(self, e):  # 关闭事件
        self.mapTool.reset()  # 重设地图工具
        e.accept()  # 接受关闭事件

    def addLayoutBotton(self, fieldName):  # 添加一个带有字段名的控件(标签+输入框)到布局
        tempLayout = QtWidgets.QHBoxLayout()  # 创建一个水平布局
        label = QtWidgets.QLabel()  # 创建一个标签
        label.setText(fieldName)  # 设置标签的文本为字段名
        tempLayout.addWidget(label)  # 将标签添加到布局
        lineEdit = QtWidgets.QLineEdit()  # 创建一个输入框
        tempLayout.addWidget(lineEdit)  # 将输入框添加到布局
        self.attrsLayout.addLayout(tempLayout)  # 将这个含有标签和输入框的布局添加到主布局
        self.attrLineDir[fieldName] = lineEdit  # 在字典中存储字段名和对应的输入框引用

    def addFeature(self):  # 添加地图特性
        for name in self.feat.fields().names():  # 遍历所有字段
            tempLine: QLineEdit = self.attrLineDir[name]  # 获取对应字段的输入框
            if tempLine.text() != "None":  # 如果输入的不是"None"
                self.feat.setAttribute(name, tempLine.text())  # 设置字段值

        # 根据不同的地图元素类型，设置元素的几何信息，同时更新图层
        if self.mapTool.wkbType == "rectangle":
            self.feat.setGeometry(self.mapTool.r)
        elif self.mapTool.wkbType == "polygon":
            self.feat.setGeometry(self.mapTool.p)
        elif self.mapTool.wkbType == "circle":
            pointsXY = [[]]
            for point in self.mapTool.points[0:-1]:
                pointsXY[0].append(QgsPointXY(point))
            self.feat.setGeometry(QgsGeometry.fromPolygonXY(pointsXY))
        self.mapTool.editLayer.addFeature(self.feat)
        self.mapTool.canvas.refresh()
        self.mapTool.reset()
        self.close()

    def initUI(self):  # 初始化UI
        self.setWindowTitle("属性编辑")  # 设置窗口标题为"属性编辑"
        self.attrLineDir = {}  # 初始化字典，用于存储每个字段名和对应输入框的引用
        for name in self.feat.fields().names():  # 遍历所有字段
            self.addLayoutBotton(name)  # 添加每个字段到布局

    def connectFunc(self):  # 连接函数
        self.add.clicked.connect(self.addFeature)  # 当点击"添加"按钮时，连接到addFeature函数
        self.cancel.clicked.connect(self.close)  # 当点击"取消"按钮时，关闭窗口